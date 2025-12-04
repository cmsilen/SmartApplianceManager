from sklearn.model_selection import train_test_split

class LearningSetsGenerator:

    def __init__(self):
        pass

    def generate_learning_sets(self, dataset):
        data = []

        for prepared_session in dataset:
            session_id, *features, label = prepared_session
            ps = {
                "features": features,
                "label": label
            }
            data.append(ps)

        train_val, test = train_test_split(
            data,
            test_size=0.1,
            shuffle=True,
            random_state=42
        )

        train, validation = train_test_split(
            train_val,
            test_size=1/9,
            shuffle=True,
            random_state=42
        )

        return {
            'training': train,
            'test': test,
            'validation': validation
        }
