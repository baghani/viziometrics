# Image Processing Models and Machine Learning Models
# 1. FeatureDescriptor: Feature images
# 2. SVM Classifier: SVM-based classifier
# 3. Convolusion Neural Network: No implemented yet

from Dictionary import *
from Options import *

# SVM Classifier
from sklearn.externals import joblib
from sklearn import svm
from sklearn import cross_validation
from sklearn import grid_search
from sklearn import metrics
from sklearn.preprocessing import LabelBinarizer
from sklearn.cross_validation import KFold


# import csv
# import itertools



# This class needs a given path to dictionary
class FeatureDescriptor():
    
    def __init__(self, dicPath):
        
        try:
            self.dicPath = dicPath
            dicPath = os.path.join(dicPath, 'dictionaryModel.npz')
            dictionary = np.load(dicPath)
            print 'Dictionary loaded from', dicPath
            self.rf = dictionary['rfSize']
            self.finalDim = dictionary['finalDim']
            self.M = dictionary['Mean']
            self.P = dictionary['Patch']
            self.whitening = dictionary['whitening']
            self.centroids = dictionary['centroids']
            self.Ncentroids = dictionary['Ncentroids']
            self.FSMean = dictionary['FSMean']
            self.FSSd = dictionary['FSSd']
            
            if self.FSMean == 'unavailable':
                print 'Feature Descriptor is not available'
                self.unTrained = True
            else:
                self.unTrained = False
            
        except:
            print 'Unable to load dictionary'
        
    @ staticmethod
    def getFeatureNames(Ncentroids):
            
        featureNames = []
        for i in range(1, Ncentroids+1):
            name = 'centroids_' + str(i)
            featureNames.append(name)
        return np.asmatrix(featureNames).T
    
    @ staticmethod 
    def im2col(Im, block, style='sliding'):

        bx, by = block
        Imx, Imy = Im.shape
        colH = (Imx - bx + 1) * (Imy - bx + 1)
        colW = bx * by 
        imCol = np.zeros((colH, colW))
        curCol = 0
        for j in range(0, Imy):
            for i in range(0, Imx):
                if (i+bx <= Imx) and (j+by <= Imy):
                    imCol[curCol, :] = Im[i:i+bx, j:j+by].T.reshape(bx*by)
                    curCol += 1
                else:
                    break
        return np.asmatrix(imCol)
    
    @ staticmethod
    def subdivPooling(X, l):
        n = np.min(X.shape[0:2])
        split = int(round(float(n)/2))
        
        if l == 0:

            Q = np.asmatrix(np.squeeze(np.sum(np.sum(X, axis = 0), axis = 0)))
            
            return Q.T
    
        else:
            nx, ny, nz = X.shape
            Q = FeatureDescriptor.subdivPooling(X[0:split, 0:split, :], l-1)
            Q = np.vstack((Q, FeatureDescriptor.subdivPooling(X[split:nx, 0:split, :], l-1)))
            Q = np.vstack((Q, FeatureDescriptor.subdivPooling(X[0:split, split:ny, :], l-1)))
            Q = np.vstack((Q, FeatureDescriptor.subdivPooling(X[split:nx, split:ny, :], l-1)))
 
        return Q
    
    def extractSingleImageFeatures (self, X, subdivLevels = 1):
        
        if not self.unTrained:
            Nimages = 1
    
            cc = np.asmatrix(np.sum(np.power(self.centroids,2), axis = 1).T)
            sz = self.finalDim[0] * self.finalDim[1]
    
            XC = np.zeros((Nimages, (4**subdivLevels)*self.Ncentroids))
    
            ps = FeatureDescriptor.im2col(np.reshape(X[0,0:sz], self.finalDim[0:2], 'F'), (self.rf, self.rf))
            ps = np.divide(ps - np.mean(ps, axis = 1), np.sqrt(np.var(ps, axis = 1) +1))
    
            if self.whitening:
                ps = np.dot((ps - self.M), self.P)
                
            xx = np.sum(np.power(ps, 2), axis = 1)
            xc = np.dot(ps, self.centroids.T)
            z = np.sqrt(cc + xx - 2*xc)
    
            v = np.min(z, axis = 1)
            inds = np.argmin(z, axis = 1)#
            mu = np.mean(z, axis = 1)
            ps = mu - z
            ps[ps < 0] = 0
    
            off = np.asmatrix(range(0, (z.shape[0])*self.Ncentroids, self.Ncentroids))
            ps = np.zeros((ps.shape[0]*ps.shape[1],1))
            ps[off.T + inds] = 1
            ps = np.reshape(ps, (z.shape[1],z.shape[0]), 'F').T#
    
                    
            prows = self.finalDim[0] - self.rf + 1
            pcols = self.finalDim[1]- self.rf + 1
            ps = np.reshape(ps, (prows, pcols, self.Ncentroids), 'F')
                    
            XC[0, :] = FeatureDescriptor.subdivPooling(ps, subdivLevels).T
        
            XCs = np.divide(XC - self.FSMean, self.FSSd)
            return XCs
        else:
            print 'FSMean and FSSd are not available, please trained model first'
        
        
    def extractFeaturesPlus(self, X, subdivLevels = 1):
        print 'Extracting feature vectors using centroid PatchSet and effective region mask...'
        startTime = time.time()
        
        Nimages = X.shape[0]

        cc = np.asmatrix(np.sum(np.power(self.centroids,2), axis = 1).T)
        sz = self.finalDim[0] * self.finalDim[1]

        XC = np.zeros((Nimages, (4**subdivLevels)*self.Ncentroids))
        
        
        for i in range(0, Nimages):
            
            if np.mod(i, 100) == 0:
                print 'Extracting features:', i, '/', Nimages

            ps = FeatureDescriptor.im2col(np.reshape(X[i,0:sz], self.finalDim[0:2], 'F'), (self.rf, self.rf))
            ps = np.divide(ps - np.mean(ps, axis = 1), np.sqrt(np.var(ps, axis = 1) +1))
            if self.whitening:
                ps = np.dot((ps - self.M), self.P)

            xx = np.sum(np.power(ps, 2), axis = 1)
            xc = np.dot(ps, self.centroids.T)
            z = np.sqrt(cc + xx - 2*xc)

            v = np.min(z, axis = 1)
            inds = np.argmin(z, axis = 1)#
            mu = np.mean(z, axis = 1)
            ps = mu - z
            ps[ps < 0] = 0
#             print 'there'
            off = np.asmatrix(range(0, (z.shape[0])*self.Ncentroids, self.Ncentroids))
            ps = np.zeros((ps.shape[0]*ps.shape[1],1))
            ps[off.T + inds] = 1
            ps = np.reshape(ps, (z.shape[1],z.shape[0]), 'F').T#

                
            prows = self.finalDim[0] - self.rf + 1
            pcols = self.finalDim[1]- self.rf + 1
            ps = np.reshape(ps, (prows, pcols, self.Ncentroids), 'F')
                
            XC[i, :] = FeatureDescriptor.subdivPooling(ps, subdivLevels).T
            
        print 'Extracting features:', i+1, '/', Nimages    
        endTime = time.time()
        print X.shape[0], 'feature vectors computed in', endTime-startTime, 'sec\n'
        
        if self.unTrained:
            print 'Updated dictionary....'
            self.FSMean = np.mean(XC, axis = 0)
            self.FSSd = np.sqrt(np.var(XC, axis = 0) + 0.01)
            self.saveDictionaryToFile() 
        else:
            print 'Normalized by trained features'
            
        XCs = np.divide(XC - self.FSMean, self.FSSd)
            
        return XCs
    
    
    def extractFeatures(self, X, subdivLevels = 1):
        
        print 'Extracting feature vectors using centroid PatchSet...'
        startTime = time.time()
        
        Nimages = X.shape[0]

        cc = np.asmatrix(np.sum(np.power(self.centroids,2), axis = 1).T)
        sz = self.finalDim[0] * self.finalDim[1]

        XC = np.zeros((Nimages, (4**subdivLevels)*self.Ncentroids))
        
        
        for i in range(0, Nimages):
            
            if np.mod(i, 100) == 0:
                print 'Extracting features:', i, '/', Nimages

            ps = FeatureDescriptor.im2col(np.reshape(X[i,0:sz], self.finalDim[0:2], 'F'), (self.rf, self.rf))
            ps = np.divide(ps - np.mean(ps, axis = 1), np.sqrt(np.var(ps, axis = 1) +1))
            if self.whitening:
                ps = np.dot((ps - self.M), self.P)

            xx = np.sum(np.power(ps, 2), axis = 1)
            xc = np.dot(ps, self.centroids.T)
            z = np.sqrt(cc + xx - 2*xc)

            v = np.min(z, axis = 1)
            inds = np.argmin(z, axis = 1)#
            mu = np.mean(z, axis = 1)
            ps = mu - z
            ps[ps < 0] = 0
#             print 'there'
            off = np.asmatrix(range(0, (z.shape[0])*self.Ncentroids, self.Ncentroids))
            ps = np.zeros((ps.shape[0]*ps.shape[1],1))
            ps[off.T + inds] = 1
            ps = np.reshape(ps, (z.shape[1],z.shape[0]), 'F').T#

                
            prows = self.finalDim[0] - self.rf + 1
            pcols = self.finalDim[1]- self.rf + 1
            ps = np.reshape(ps, (prows, pcols, self.Ncentroids), 'F')
                
            XC[i, :] = FeatureDescriptor.subdivPooling(ps, subdivLevels).T
            
        print 'Extracting features:', i+1, '/', Nimages    
        endTime = time.time()
        print X.shape[0], 'feature vectors computed in', endTime-startTime, 'sec\n'
        
        if self.unTrained:
            print 'Updated dictionary....'
            self.FSMean = np.mean(XC, axis = 0)
            self.FSSd = np.sqrt(np.var(XC, axis = 0) + 0.01)
            self.saveDictionaryToFile() 
        else:
            print 'Normalized by trained features'
            
        XCs = np.divide(XC - self.FSMean, self.FSSd)
            
        return XCs
    
    def saveDictionaryToFile(self):
        print 'Saving dictionary...'   
        filePath = os.path.join(self.dicPath, 'dictionaryModel')
        np.savez(filePath,
                 rfSize = self.rf,
                 finalDim = self.finalDim,
                 whitening = self.whitening,
                 Ncentroids = self.Ncentroids,
                 Mean = self.M,
                 Patch = self.P,
                 centroids = self.centroids,
                 FSMean = self.FSMean,
                 FSSd = self.FSSd
                 )
         
        print 'Dictionary Updated in', self.dicPath, '\n'
        return self.dicPath

class SVMClassifier:
    
    clssifier = None
    modelTrained = False
    modelOptimized = False
    Opt = None
    
    def __init__(self, Opt, isTrain = None, clfPath = None):
        
        self.Opt = Opt
        if isTrain is None:
            isTrain = Opt.isTrain
        
        if isTrain is False:
            if clfPath is None:
                clfPath = Opt.svmModelPath
            try:     
                clfPath = os.path.join(clfPath, 'SVMModel.pkl')
                print 'Loading classifier from', clfPath
                self.classifier = joblib.load(clfPath)
                self.modelTrained = True
                
                print 'SVM Classifier loaded.'
            except:
                print 'Unable to read the trained model'
                
        else:
            if Opt.isTrain:
                print 'Untrained SVM created.'
            else:
                print 'Options is not in train mode'

    def loadSVNModel(self, modelPath):
        return 
        
    
    def saveSVMModel(self, path = None):
        
        if path is None:
            path = self.Opt.modelPath
        
        if self.modelTrained:
            print 'Saving SVM model...'
            infoFilePath = os.path.join(path, 'SVMModelInfo')
            clfFilePath = os.path.join(path, 'SVMModel.pkl') 
            joblib.dump(self.classifier, clfFilePath)
            
            print 'SVMModel.pkl and SVMModelInfo.pkl were saved in', path
            return path
        else:
            print 'Model has not been trained first.'
    
    
    def saveEvaluation(self, y_test, y_pred, path = None, mode = "wb"):
        
        if self.Opt.isTrain:
            if path is None:
                path = self.Opt.modelPath
        else:
            if path is None:
                path = self.Opt.svmModelPath           
            
        if self.modelOptimized or not self.Opt.isTrain:
            
            confusionMat = metrics.confusion_matrix(y_test, y_pred)
            confusionMat = np.asmatrix(confusionMat)
            
            allScores = metrics.precision_recall_fscore_support(y_test, y_pred, average=None)
            
            for j in range(1,3):
                values = np.asmatrix(allScores[j]).T
                confusionMat = np.hstack([confusionMat, values])
                   
            lastRow = np.hstack([allScores[0] ,[0, 0]])
            confusionMat = np.vstack([confusionMat, lastRow])
            confusionList = confusionMat.tolist()
            
            firstCol = sorted(self.Opt.classNames[:])
            firstCol.append('precision')
            for i in range(0, len(confusionList)):
                confusionList[i].insert(0, firstCol[i])
            
            head = sorted(self.Opt.classNames[:])
            head.insert(0, '')
            head.extend(['recall', 'f1_score'])
            
            confusionList.insert(0, head)
            
            if self.Opt.isTrain:
                filename = 'model_evaluation'
            else:
                filename = 'model_evaluation_test_' + datetime.datetime.now().strftime("%Y-%m-%d")
            Common.saveCSV(path, filename, confusionList, mode = mode)
            
        else:
            print 'Model has not been trained first.'
    
    def predict(self, X_test):
                    
        if self.modelTrained:
            pred_label = self.classifier.predict(X_test)
            pred_probability = self.classifier.predict_proba(X_test)
            return pred_label, pred_probability
        else:
            print 'Model has not been trained first.'
        
    
    def evaluate(self, y_true, y_pred, y_proba, save = False, path = None):
        
        accuracy = metrics.accuracy_score(y_true, y_pred)
        precision = metrics.precision_score(y_true, y_true, average=None)
        recall = metrics.recall_score(y_true, y_true, average=None)
#         result = zip(self.classNames, precision, recall)
        
        print "Accruracy:", accuracy
#         print "(Class, precision, recall)", result
        
        if save:
            if path is None:
                path = self.Opt.svmModelPath
                
            print_result = [['Accuracy From %d Testing Image:'%len(y_true), accuracy]]
            
            if self.Opt.isTrain:
                filename = 'model_evaluation'
            else:
                filename = 'model_evaluation_test_' + datetime.datetime.now().strftime("%Y-%m-%d")
                
            Common.saveCSV(path, filename, print_result, mode = 'ab')
        
        print metrics.classification_report(y_true, y_pred)
        
        
    def evaluateCVModelByHeldOutData(self, X_train, y_train, X_test, y_test, path = None, showIterationResult = False):
        
        if self.modelOptimized:
            print("Best parameters set found on development set:")
            print self.classifier.best_estimator_, '\n'
              
            # Quantitative evaluation
#             scores = self.getTenFoldValidation(X_train, y_train)
#             print("Holdout training data: 10-Fold cross-validation accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
            y_pred = self.classifier.predict(X_test)
            print 'Holdout testing data accuracy:', self.classifier.score(X_test, y_test)
            print "Holdout testing data report:"
            print metrics.classification_report(y_test, y_pred), '\n'
               
            if showIterationResult:
                print("Grid scores on development set:")
                for params, mean_score, scores in self.classifier.grid_scores_:
                    print("%0.3f (+/-%0.03f) for %r" % (mean_score, scores.std() / 2, params))
                    print() 

            self.saveEvaluation(y_test, y_pred, path = path)
        else:
            print 'Model has not been trained.\n'
    
    def getTenFoldConfusionMatrix(self, X, Y, path = None):
        
        if self.modelOptimized:
            print "Evaluating 10-fold confusion matrix..."
            k_fold = KFold(n=X.shape[0], shuffle = True, n_folds = 10)
            count = 0
            
            all_y_test = None
            all_y_pred = None
            for train_indices, test_indices in k_fold:
                print "Computing fold No. %d" %count
                count += 1
                       
                x_train = X[train_indices]
                y_train = Y[train_indices]
                
                x_test = X[test_indices]
                y_test = Y[test_indices]
                
                self.classifier.fit(x_train, y_train)
                y_pred = self.classifier.predict(x_test)
                
                if count == 1:
                    all_y_pred = y_pred
                    all_y_test = y_test
                else:
                    all_y_pred = np.hstack([all_y_pred, y_pred])
                    all_y_test = np.hstack([all_y_test, y_test])
                              
            print "10-fold testing data report:"
            print metrics.classification_report(all_y_test, all_y_pred), '\n'
        
            if path is not None:
                self.saveEvaluation(all_y_test, all_y_pred, path = path, mode = "ab")              
        else:
            print 'Model has not been trained.\n'
        
    
    def getTenFoldValidation(self, X, Y, path):
        if self.modelOptimized:
            accuracy = cross_validation.cross_val_score(self.classifier.best_estimator_, X, Y, cv=10)
            
            lb = LabelBinarizer()
            y = np.array([number[0] for number in lb.fit_transform(Y)])
            recall = cross_validation.cross_val_score(self.classifier.best_estimator_, X, y, cv=10, scoring='recall')
            precision = cross_validation.cross_val_score(self.classifier.best_estimator_, X, y, cv=10, scoring='precision')
            f1_score = cross_validation.cross_val_score(self.classifier.best_estimator_, X, y, cv=10, scoring='f1')
            
            
            items = ["accuracy", "recall", "precision", "f1_score"]
            result = (accuracy, recall, precision, f1_score)
            for i in range(0, 4):
                print "Tuned Model: 10-Fold cross-validation %s: %0.2f (+/- %0.2f)" % (items[i], result[i].mean(), result[i].std() * 2)
                print_result = [['Cross-Validation', 'Full Data', '%s:'% items[i], result[i].mean(), result[i].std()*2]]
                Common.saveCSV(path, 'model_evaluation', print_result, mode = 'ab')
                
            return (accuracy, recall, precision, f1_score)
        else:
            print 'Model has not been trained.\n'
        
    def trainModel(self, X, y, outModelPath = None):
        
        if outModelPath is None:
            outModelPath = self.Opt.modelPath
            
        print 'Training Model...'
        startTime = time.time()

        # Split into training and test set (e.g., 75/25)
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.25, random_state=0)
        
        # Choose estimator
        self.estimator = svm.SVC(probability = True)
#         self.estimator = svm.SVC(kernel = 'linear', probability = True)
        
        # Choose cross-validation iterator
        cv = cross_validation.ShuffleSplit(X_train.shape[0], n_iter=10, test_size=0.25, random_state=0)
        
        
        # Tune the hyperparameters
#         gammas = np.logspace(-6, -1, 10)
#         self.classifier = grid_search.GridSearchCV(estimator=self.estimator, cv=cv, param_grid=dict(gamma=gammas))
#         tuned_parameters = [{'kernel': ['rbf'], 'gamma': [0, 1e-3, 1e-4], 'C': [1, 10]},]
#         tuned_parameters = [{'kernel': ['rbf', 'linear', 'poly'], 'gamma': [1e-3, 1e-4], 'C': [1, 10, 100, 1000]},]
        tuned_parameters = self.Opt.tuned_parameters 
        self.classifier = grid_search.GridSearchCV(estimator = self.estimator, cv = cv, param_grid = tuned_parameters)     
        
        # Train the optimized model with the split training set
        self.classifier.fit(X_train, y_train)
        self.modelOptimized = True
        
        # Evaluate and Save Cross-validation model by holdout test data
        self.evaluateCVModelByHeldOutData(X_train, y_train, X_test, y_test, path = outModelPath)
         
        # Evaluate and Save Cross-validation model by 10-fold on the full data
        self.getTenFoldConfusionMatrix(X, y, path = outModelPath)
         
        # Train final model with the full training set
        print 'Train final model with the full training set...'
        self.classifier.fit(X, y)
        self.modelTrained = True
        print 'Tuned Model: Full training data accuracy:', self.classifier.score(X, y)
        scores = self.getTenFoldValidation(X, y, path = outModelPath)
#         accraucy = scores[0]
#         recall = scores[1]
#         precision = scores[2]
#         f1_score = scores[3]
#         print "Tuned Model: 10-Fold cross-validation accuracy: %0.2f (+/- %0.2f)" % (accraucy.mean(), accraucy.std() * 2)
#         print "Tuned Model: 10-Fold cross-validation recall: %0.2f (+/- %0.2f)" % (recall.mean(), recall.std() * 2)
#         print recall
#         print "Tuned Model: 10-Fold cross-validation precision: %0.2f (+/- %0.2f)" % (precision.mean(), precision.std() * 2)
#         print precision
#         print "Tuned Model: 10-Fold cross-validation f1_score: %0.2f (+/- %0.2f)" % (f1_score.mean(), f1_score.std() * 2)
#         print f1_score
#         
#         result_accuracy = [['Cross-Validation', 'Full Data', 'Accuracy:', accraucy.mean(), accraucy.std()*2]]
#         Common.saveCSV(outModelPath, 'model_evaluation', result_accuracy, mode = 'ab')
#         result_recall = [['Cross-Validation', 'Full Data', 'Recall:', recall.mean(), recall.std()*2]]
#         Common.saveCSV(outModelPath, 'model_evaluation', result_recall, mode = 'ab')
#         result_precision = [['Cross-Validation', 'Full Data', 'Precision:', precision.mean(), precision.std()*2]]
#         Common.saveCSV(outModelPath, 'model_evaluation', result_precision, mode = 'ab')
#         result_f1_score = [['Cross-Validation', 'Full Data', 'f1_score:', f1_score.mean(), f1_score.std()*2]]
#         Common.saveCSV(outModelPath, 'model_evaluation', result_f1_score, mode = 'ab')
        
        endTime = time.time()
        print 'Complete training model in ',  endTime - startTime, 'sec\n'
        
        return self.saveSVMModel(path = outModelPath) 
