from sklearn.preprocessing import StandardScaler

data = pd.read_csv('default_of_credit_card_clients.csv')
data.head()

y = data['target'].values
X = data.drop(['target'], axis=1).values

Xtrain, Xvalidate, ytrain, yvalidate = train_test_split(X, y, 
                                                        test_size=0.50, 
                                                        random_state=42)

Xvalidate, Xtest, yvalidate, ytest  = train_test_split(Xvalidate, yvalidate, 
                                                        test_size=0.40, 
                                                        random_state=42)

baseline_mod = DummyClassifier()
baseline_mod.fit(Xtrain, ytrain)
print("The training score is: ", baseline_mod.score(Xtrain, ytrain))
print("The validation score is: ", baseline_mod.score(Xvalidate, yvalidate))
print("The testing score is: ", baseline_mod.score(Xtest, ytest))