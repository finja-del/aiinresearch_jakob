import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import numpy as np

class QualityIndex:
    # Class: Predict academic paper quality
    
    def __init__(self, features, target, model_params=None):
        # Step 1: Initialize predictor
        # Store features and target column names
        self.features = features
        self.target = target
        # Set up Decision Tree Regressor model parameters
        self.model_params = model_params if model_params is not None else {'max_depth': 7, 'random_state': 42}
        self.model = DecisionTreeRegressor(**self.model_params)
        # Initialize internal data storage
        self.df = None
        self.X_train, self.X_test, self.y_train, self.y_test = None, None, None, None
        self.imputer = None # For handling missing values
        print('QualityIndex predictor initialized.')

    def load_data(self, csv_file_path=None, num_synthetic_samples=500):
        # Step 2: Load or create data
        self.df = None # Clear existing data

        # Try loading from CSV first
        if csv_file_path:
            try:
                self.df = pd.read_csv(csv_file_path)
                print(f'Data loaded from {csv_file_path}. Shape: {self.df.shape}')
                # Validate required columns
                missing_cols = [col for col in self.features + [self.target] if col not in self.df.columns]
                if missing_cols:
                    raise ValueError(f'Missing required columns in CSV: {missing_cols}')
                print(f'First 5 rows of loaded data:\n{self.df.head()}')
            except FileNotFoundError:
                print(f'Warning: CSV file not found at {csv_file_path}. Falling back to synthetic data.')
            except ValueError as e:
                print(f'Data loading error from CSV: {e}. Falling back to synthetic data.')

        # If CSV not loaded, generate synthetic data
        if self.df is None:
            np.random.seed(self.model_params.get('random_state', 42))
            synthetic_data = {
                'recency': np.random.randint(1, 15, num_synthetic_samples),
                'journal_index': np.random.uniform(0.5, 10.0, num_synthetic_samples),
                'h_index': np.random.randint(5, 80, num_synthetic_samples),
                'citations': np.random.randint(0, 1000, num_synthetic_samples)
            }
            self.df = pd.DataFrame(synthetic_data)
            # Introduce some missing h_index values for testing imputation
            missing_h_index_indices = np.random.choice(self.df.index, size=int(0.1 * num_synthetic_samples), replace=False)
            self.df.loc[missing_h_index_indices, 'h_index'] = np.nan
            print(f'Introduced {len(missing_h_index_indices)} missing h_index values in synthetic data.')

            # Generate synthetic target values
            self.df[self.target] = (
                (10 * self.df['journal_index']) +
                (0.5 * self.df['h_index'].fillna(0)) + 
                (0.01 * self.df['citations']) -
                (1.5 * self.df['recency']) +
                np.random.normal(0, 5, num_synthetic_samples)
            )
            self.df[self.target] = self.df[self.target].apply(lambda x: max(0, x)).round(2)
            print(f'Synthetic dataset created with {num_synthetic_samples} samples.')
            print(f'First 5 rows of synthetic data:\n{self.df.head()}')
            print('\nMissing values after synthetic data generation (before imputation):')
            print(self.df.isnull().sum())

        # If data is ready, proceed to preprocessing and splitting
        if self.df is not None:
            self.preprocess_data()
            self._prepare_data_for_training()

        else:
            return False

    def preprocess_data(self):
        # Step 3: Handle missing data, fills in missing numerical values
        
        if self.df is None:
            print('No data to preprocess.')
            return

        print('\n--- Preprocessing Data (Handling Missing Values) ---')
        numerical_features = [f for f in self.features if self.df[f].dtype in ['int64', 'float64']]

        if numerical_features:
            self.imputer = SimpleImputer(strategy='median') # Use median for imputation
            self.imputer.fit(self.df[numerical_features])
            self.df[numerical_features] = self.imputer.transform(self.df[numerical_features])
            print(f'Missing numerical values imputed using {self.imputer.strategy_} strategy.')
        else:
            print('No numerical features to impute.')

        print('\nMissing values after imputation:')
        print(self.df.isnull().sum())

    def _prepare_data_for_training(self):
        # Step 4: Prepare and split data, separates features (X) from target (y) and split into training/testing sets
        if self.df is None:
            print('No data loaded. Cannot prepare data for training.')
            return

        X = self.df[self.features] # Select feature columns
        y = self.df[self.target]   # Select target column

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.3, random_state=self.model_params.get('random_state', 42)
        )
        print(f'\nData prepared and split:')
        print(f'Training set size: {self.X_train.shape[0]} samples')
        print(f'Test set size: {self.X_test.shape[0]} samples')

    def train_model(self):
        # Step 5: Train the model, builds the Decision Tree Regressor using training data
        if self.X_train is None or self.y_train is None:
            print('Training data not prepared. Call load_data() first.')
            return

        print('\n--- Training Decision Tree Regressor model... ---')
        self.model.fit(self.X_train, self.y_train)
        print('Model training complete.')

    def evaluate_model(self):
        # Step 6: Evaluate model performance, unsure if this is needed. It assess how well the model predicts on unseen test data
        
        if self.model is None or self.X_test is None or self.y_test is None:
            print('Model not trained or test data not available. Call train_model() first.')
            return

        print('\n--- Model Evaluation ---')
        y_pred = self.model.predict(self.X_test)

        mse = mean_squared_error(self.y_test, y_pred)
        r2 = r2_score(self.y_test, y_pred)
        print(f'Mean Squared Error (MSE): {mse:.2f}')
        print(f'R-squared (R2): {r2:.2f}')

        # Visualize actual vs. predicted values
        plt.figure(figsize=(10, 6))
        plt.scatter(self.y_test, y_pred, alpha=0.6)
        plt.plot([self.y_test.min(), self.y_test.max()], [self.y_test.min(), self.y_test.max()], 'r--', lw=2)
        plt.xlabel(f'Actual {self.target}')
        plt.ylabel(f'Predicted {self.target}')
        plt.title(f'Actual vs. Predicted {self.target} (R2: {r2:.2f})')
        plt.grid(True)
        plt.show()

    def provide_parameter_weightage(self):
        # Step 7: Show parameter influence, Display how important each feature was in making predictions
        
        if self.model is None:
            print('Model not trained. Cannot provide parameter weightage.')
            return

        print('\n--- Parameter Weightage (Feature Importance) ---')
        if not hasattr(self.model, 'feature_importances_'):
            print('The trained model does not have #feature_importances# attributes.')
            print('This usually means it\'s not a tree-based model or it hasn\'t been fitted.')
            return

        feature_importances = pd.Series(self.model.feature_importances_, index=self.features)
        feature_importances_sorted = feature_importances.sort_values(ascending=False)

        print('The weightage (importance) of each parameter in determining the paper\'s quality index:')
        for feature, importance in feature_importances_sorted.items():
            print(f'- {feature.replace("_", " ").title()}: {importance:.4f}')

        # Interpret the most influential parameter
        if not feature_importances_sorted.empty:
            most_important = feature_importances_sorted.index[0]
            print(f'\nInterpretation: The {most_important.replace("_", " ").lower()} parameter has the highest influence ({feature_importances_sorted.iloc[0]:.4f}) on the predicted quality index, according to this model.')
        else:
            print('No feature importances found.')


    def predict_quality(self, new_paper_data):
        # Step 8: Make new predictions
        # Use the trained model to predict quality for new, unseen papers
        
        if self.model is None:
            print('Model not trained. Please train the model before making predictions.')
            return None
        if self.imputer is None:
            print('Imputer not fitted. Data preprocessing was not performed. Cannot make predictions.')
            return None

        # Convert new data to DataFrame
        if isinstance(new_paper_data, dict):
            new_df = pd.DataFrame([new_paper_data], columns=self.features)
        elif isinstance(new_paper_data, list):
            new_df = pd.DataFrame(new_paper_data, columns=self.features)
        else:
            raise ValueError('Input #new_paper_data# must be a dict or a list of dicts.')

        # Handle any missing required features in new data
        for mf in self.features:
            if mf not in new_df.columns:
                new_df[mf] = np.nan

        # Ensure column order matches training data
        new_df = new_df[self.features]

        # Apply the #trained# imputer to fill missing values in new data
        numerical_features_in_new_df = [f for f in self.features if f in new_df.columns and new_df[f].dtype in ['int64', 'float64', 'float32']]

        if self.imputer and numerical_features_in_new_df:
            new_df[numerical_features_in_new_df] = self.imputer.transform(new_df[numerical_features_in_new_df])
        else:
            if new_df.isnull().any().any():
                print('Warning: New data contains NaNs that could not be imputed. Model might error.')

        return self.model.predict(new_df)