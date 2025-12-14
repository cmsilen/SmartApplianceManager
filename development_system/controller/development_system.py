import os
import sys
import time
from threading import Thread
from development_system.controller.testing_controller import TestController
from development_system.controller.training_controller import TrainingController
from development_system.controller.validation_controller import ValidationController
# from development_system.fake_data.load_FakeDataset import load_learning_data_from_json
from development_system.model.communication_config import CommunicationConfig
from development_system.model.communication_manager import CommunicationManager
from development_system.model.learning_set_data import LearningDataSet
from development_system.model.smart_classifier import SmartClassifier
from development_system.model.system_configuration import DevSystemConfig

#
STAGES = ["waiting" , "set_avg_hyp" , "set_num_iters", "train", "set_hyp",
          "gen_learn_report" ,
          "gen_vld_report" , "gen_test_report" , "config_sent" , "send_classifier"]



class DevelopmentSystemOrchestrator:

    def __init__(self):
        print("[INFO] STARTING THE DEVELOPMENT SYSTEM...")
        self.system_conf = DevSystemConfig()
        self.communication_config = CommunicationConfig()
        self.smart_classifier = SmartClassifier()
        self.training_controller = TrainingController()
        self.winner_uuid = None


    def update_stage(self, new_stage):
        self.system_conf.stage = new_stage
        self.system_conf.update_stage()

    def run(self, automated=False):  #
        print("IN SIDE RUN")
        """
        :param automated==False ...  means  manual
        :return:
        """

        # Grab the IP and Port of the development system from the CommunicationConfig Class.

        print("CURRENT STAGE: ", self.system_conf.stage)

        # Grab the IP and port of the development system from the CommunicationConfig Class

        dev_system_ip, dev_system_port = self.communication_config.get_ip_port("development_system")

        print("dev sys ip ",dev_system_ip)
        print("dev sys port ",dev_system_port)

        if not automated:
            # Start listener in Background (simulates CommunicationManager)
            run_thread = Thread(target=CommunicationManager.get_instance().listener,
                                args=(dev_system_ip, dev_system_port))
            run_thread.daemon = True
            run_thread.start()

        while True:
            # From the Development system bpmn diagram a calibration set is arrived at the JsonIO end point. i.e the
            # MessageManager class
            # --> So we follow all the paths that the bpmn has set to fulfill the requirements.

            # 1️ Receive Calibration Set Data
            if self.system_conf.stage == "waiting":
                print(f"WAITING STAGE")
                dataset = CommunicationManager.get_instance().get_queue().get(block=True)
                LearningDataSet.set_data(dataset)
                self.update_stage("set_avg_hyp")

            # 2️ Set Average Hyperparameters
            if self.system_conf.stage == "set_avg_hyp":
                print("[INFO] Setting average hyperparameters...")
                self.training_controller.set_avg_hyper_params()
                print("[INFO] Average hyperparameters set.")
                self.update_stage("set_num_iters")

            # 3️ Ask for number of iterations
            if self.system_conf.stage == "set_num_iters":
                if automated:
                    inserted_iterations = 5
                else:
                    try:
                        inserted_iterations = int(input("[HUMAN] Insert number of iterations: "))
                    except ValueError:
                        print("[WARN] Invalid input, using default 5.")
                        inserted_iterations = 40
                self.training_controller.update_num_iterations(inserted_iterations)
                self.update_stage("train")
            # 4️ Train the model
            if self.system_conf.stage == "train":
                print("[INFO] Starting training...")
                self.training_controller.train_model()
                self.update_stage("gen_learn_report")

            # 5️ Generate Learning Report and wait for Data Scientist Decision
            if self.system_conf.stage == "gen_learn_report":
                self.training_controller.generate_calibration_report()
                print("[INFO] Training chart exported. Waiting for DS to review...")

                if automated:
                    learning_res = "y"
                else:
                    print(" ")
                    learning_res = input("[Human] Is the number of iterations fine? (Y/n): ")
                if learning_res.lower() == "y":
                    self.system_conf.ongoing_validation = False
                    self.update_stage("set_hyp")
                else:
                    self.update_stage("set_num_iters")

            # 6️ Validation Phase
            if self.system_conf.stage == "set_hyp":
                print("[INFO] Starting validation phase...")
                validation_controller = ValidationController()
                validation_controller.get_classifiers()  # runs grid search
                validation_controller.get_validation_report()
                if automated:  # used for python test of the classifier
                    self.winner_uuid = "NN50" # local test
                    self.update_stage("gen_test_report")
                else:
                    self.winner_uuid = input("[HUMAN] Insert the UUID of the winner classifier: ").strip()
                    if not self.winner_uuid:
                        self.update_stage("set_avg_hyp")
                    else:
                        validation_controller.get_the_winner_classifier(self.winner_uuid)
                        self.update_stage("gen_test_report")

            # 7️ Test Phase
            if self.system_conf.stage == "gen_test_report":
                print("[INFO] Running test phase...")
                testing_controller = TestController()
                testing_controller.evaluate_test_results()
                testing_controller.generate_test_results()
                print("[INFO] Test report generated. Waiting for DS evaluation.")
                if automated:
                    test_res = "y"
                else:
                    test_res = input("[HUMAN] Is the test passed? (Y/n): ")
                if test_res.lower() == "y":
                    print("Test Passed!")
                    self.update_stage("send_classifier")
                else:
                    print("Test Failed!")
                    self.update_stage("config_sent")
                if automated:
                    break

            # 8️ If Test Failed we gonna request new Configuration
            if self.system_conf.stage == "config_sent":
                print("[WARN] Test not passed. Reconfiguration required.")
                self.update_stage("waiting")
                print("[WARN] The Development system shuts Down.Bye!")
                sys.exit(1)

                # 9️ Send Final WinnerClassifier to Classification system
            if self.system_conf.stage == "send_classifier":
                print("[INFO] Sending classifier to production system...")
                try:
                    if automated:
                        self.winner_uuid = "NN50"
                        CommunicationManager.get_instance().send_classifier_joblib_automated(self.winner_uuid)
                        self.update_stage("waiting")
                    else:
                        CommunicationManager.get_instance().send_classifier_joblib_non_automated(self.winner_uuid)
                        self.update_stage("waiting")
                except Exception as e:
                    print(f"[ERROR] Failed to send classifier: {str(e)}")
                    print("[WARN] The Development system shuts Down.Bye!")
                    sys.exit(1)
