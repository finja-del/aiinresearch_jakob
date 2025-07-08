if __name__ == '__main__':
    # Define your paper features and the target quality score
    FEATURES = ['recency', 'journal_index', 'h_index', 'citations']
    TARGET = 'quality_index_score'

    # Step 1: Initialize the predictor
    predictor = QualityIndex(features=FEATURES, target=TARGET)

    # Step 2: Load Data (will use synthetic if CSV not found)
    predictor.load_data(num_synthetic_samples=1000)

    # Proceed if data was successfully loaded/generated
    if predictor.df is not None:
        # Step 5: Train the model
        predictor.train_model()

        # Step 6: Evaluate the model's overall performance
        predictor.evaluate_model()

        # Step 7: Get the weightage of each parameter
        predictor.provide_parameter_weightage()

        # Step 8: Make predictions for new papers
        print('\n--- Making Predictions for New Papers ---')

        new_papers_to_predict = [
            {'recency': 2, 'journal_index': 8.2, 'h_index': 70, 'citations': 450}, # High quality candidate
            {'recency': 10, 'journal_index': 1.5, 'citations': 15}, # h_index is missing here; it will be imputed
            {'recency': 4, 'journal_index': 4.0, 'h_index': 30, 'citations': 80}  # Mixed characteristics
        ]

        for i, paper_data in enumerate(new_papers_to_predict):
            try:
                predicted_score = predictor.predict_quality(paper_data)
                if predicted_score is not None:
                    print(f'\nPaper {i+1} Features: {paper_data}')
                    print(f'Predicted Quality Index: {predicted_score[0]:.2f}')
            except ValueError as e:
                print(f'\nError predicting for Paper {i+1}: {e}')
