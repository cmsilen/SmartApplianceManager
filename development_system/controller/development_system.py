import os
import sys
import random
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
STAGES = ["waiting", "set_avg_hyp", "set_num_iters", "train", "set_hyp",
          "gen_learn_report",
          "gen_vld_report", "gen_test_report", "config_sent", "send_classifier"]


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

        print("dev sys ip ", dev_system_ip)
        print("dev sys port ", dev_system_port)

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
                # dataset = {'training': [{'features': [23.0, 214.0, 43.0, 26.0, 64.0, 7.0], 'label': 'overheating'}, {'features': [22.0, 212.0, 42.0, 25.0, 61.0, 8.0], 'label': 'overheating'}, {'features': [11.0, 220.0, 28.0, 19.0, 51.0, 1.0], 'label': 'none'}, {'features': [11.0, 225.0, 29.0, 19.0, 55.0, 2.0], 'label': 'none'}, {'features': [11.0, 225.0, 30.0, 21.0, 54.0, 3.0], 'label': 'none'}, {'features': [17.0, 229.0, 34.0, 22.0, 49.0, 5.0], 'label': 'electrical'}, {'features': [10.0, 223.0, 29.0, 21.0, 52.0, 3.0], 'label': 'none'}, {'features': [9.0, 222.0, 30.0, 21.0, 53.0, 0.3], 'label': 'none'}, {'features': [26.0, 216.0, 46.0, 27.0, 66.0, 9.0], 'label': 'overheating'}, {'features': [24.0, 218.0, 44.0, 26.0, 63.0, 7.0], 'label': 'overheating'}, {'features': [13.0, 224.0, 29.0, 20.0, 54.0, 0.2], 'label': 'none'}, {'features': [12.0, 223.0, 29.0, 19.0, 51.0, 1.0], 'label': 'none'}, {'features': [14.0, 227.0, 31.0, 23.0, 47.0, 6.0], 'label': 'electrical'}, {'features': [21.0, 213.0, 41.0, 24.0, 60.0, 8.0], 'label': 'overheating'}, {'features': [16.0, 228.0, 33.0, 22.0, 48.0, 4.0], 'label': 'electrical'}, {'features': [17.0, 229.0, 34.0, 22.0, 50.0, 4.0], 'label': 'electrical'}, {'features': [14.0, 227.0, 31.0, 23.0, 47.0, 4.0], 'label': 'electrical'}, {'features': [25.0, 215.0, 45.0, 27.0, 65.0, 9.0], 'label': 'overheating'}, {'features': [15.0, 231.0, 32.0, 23.0, 48.0, 6.0], 'label': 'electrical'}, {'features': [16.0, 228.0, 33.0, 22.0, 49.0, 4.0], 'label': 'electrical'}, {'features': [15.0, 231.0, 32.0, 23.0, 48.0, 5.0], 'label': 'electrical'}, {'features': [20.0, 210.0, 40.0, 25.0, 60.0, 8.0], 'label': 'overheating'}, {'features': [9.0, 221.0, 27.0, 19.0, 50.0, 1.0], 'label': 'none'}, {'features': [10.0, 220.0, 30.0, 20.0, 50.0, 3.0], 'label': 'none'}], 'test': [{'features': [10.0, 220.0, 30.0, 20.0, 53.0, 3.0], 'label': 'none'}, {'features': [18.0, 230.0, 35.0, 22.0, 49.0, 6.0], 'label': 'electrical'}, {'features': [13.0, 222.0, 28.0, 20.0, 52.0, 2.0], 'label': 'none'}], 'validation': [{'features': [12.0, 226.0, 31.0, 20.0, 55.0, 2.0], 'label': 'none'}, {'features': [15.0, 230.0, 32.0, 21.0, 48.0, 5.0], 'label': 'electrical'}, {'features': [12.0, 221.0, 28.0, 20.0, 52.0, 0.1], 'label': 'none'}]}
                print(dataset)
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
                        # inserted_iterations = int(input("[HUMAN] Insert number of iterations: "))
                        inserted_iterations = random.randint(5, 20)
                        print(f"[HUMAN] Insert number of iterations: {inserted_iterations}")
                    except ValueError:
                        print("[WARN] Invalid input, using default 5.")
                        inserted_iterations = 40
                self.training_controller.update_num_iterations(inserted_iterations)
                self.update_stage("train")
            # 4️ Train the model
            if self.system_conf.stage == "train":
                print("[INFO] Starting training...")
                d = self.training_controller.train_model()
                print(d)
                self.update_stage("gen_learn_report")

            # 5️ Generate Learning Report and wait for Data Scientist Decision
            if self.system_conf.stage == "gen_learn_report":
                self.training_controller.generate_calibration_report()
                print("[INFO] Training chart exported. Waiting for DS to review...")

                if automated:
                    learning_res = "y"
                else:
                    print(" ")
                    # learning_res = input("[Human] Is the number of iterations fine? (Y/n): ")
                    learning_res = 'y' if random.random() < 0.9 else 'n'
                    # learning_res = 'y'
                    print(f"[HUMAN] Is the number of iterations fine? {learning_res}")
                if learning_res.lower() == "y":
                    self.system_conf.ongoing_validation = False
                    self.update_stage("set_hyp")
                else:
                    self.update_stage("set_num_iters")

            # 6️ Validation Phase
            if self.system_conf.stage == "set_hyp":
                print("[INFO] Starting validation phase...")
                validation_controller = ValidationController()
                candidate_classifiers = validation_controller.get_classifiers()  # runs grid search
                print(candidate_classifiers)
                validation_controller.get_validation_report()
                if automated:  # used for python test of the classifier
                    self.winner_uuid = "NN50"  # local test
                    self.update_stage("gen_test_report")
                else:
                    winner_classifier = random.choice(candidate_classifiers)
                    self.winner_uuid = winner_classifier["uuid"]
                    # self.winner_uuid = input("[HUMAN] Insert the UUID of the winner classifier: ").strip()
                    print(f"[HUMAN] Insert the UUID of the winner classifier: {self.winner_uuid}")
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
                    # test_res = input("[HUMAN] Is the test passed? (Y/n): ")
                    test_res = 'y' if random.random() < 0.9 else 'n'
                    # test_res = 'y'
                    print(f"[HUMAN] Is the test passed? (Y/n): {test_res}")
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
