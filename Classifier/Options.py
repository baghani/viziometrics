# from os.path import *
import cPickle as pickle
import os, errno
import datetime
import csv

# Class of all parameters
class Opt():
    def __init__(self, isTrain = False, isTest = False, isClassify = False):
        
        ## Mode
        logic = isTrain + isTest + isClassify
        if logic == 0:
            isClassify = True # Default
        elif logic > 1:
            print 'Warning! Must select either training mode or classifying mode'
        
        if isTrain:
            print 'Training Mode'
        elif isTest:
            print 'Testing Mode'
        elif isClassify:
            print 'Classifying Mode'
            
        self.isTrain = isTrain
        self.isTest = isTest
        self.isClassify = isClassify
        
        if self.isTrain  or self.isClassify:
            print 'Warning! Must select either training mode or classifying mode'
        
        ## Classifiers
        self.availableClassifiers = ['SVM', 'CNN']
        self.activatedClassifiers = 'SVM'

        ## S3 Data Read Parameter
        self.keyPath = '/Users/sephon/Desktop/Research/VizioMetrics/keys.txt'
        self.host = 'escience.washington.edu.viziometrics'

        ## Data Read Parameter
        self.finalDim = [128, 128, 1]    # Final image dimensions
#         self.Ntrain = 1                  #/ Number of training images per category
#         self.Ntest = 1                   #/ Number of test images per category
        self.validImageFormat = ['jpg', 'tif', 'bmp', 'png', 'tiff']    # Valid image formats
        self.classNames = ['photo', 'test3','scheme', 'test2', 'table', 'visualization', 'multichart']
        self.classNames = sorted(self.classNames)
        self.classIDs = range(1, len(self.classNames)+1)        # Start from 1
        self.classInfo = dict(zip(self.classNames, self.classIDs))
        
        
        ## Dictionary Parameter
        self.Npatches = 50000;           # Number of patches
        self.Ncentroids = 200;           # Number of centroids
        self.rfSize = 6;                 # Receptor Field Size (i.e. Patch Size)
        self.kmeansIterations = 100      # Iterations for kmeans centroid computation
        self.whitening = True            # Whether to use whitening
        self.normContrast = True         # Whether to normalize patches for contrast
        self.minibatch = True           # Use minibatch to train SVM 
        self.MIN_PATCH_VAR = 38/255      # Minimum Patch Variance for accepting as potential centroid (empirically set to about 25% quartile of var)
        self.kmeansIterations = 50
        
        ## SVM Classifier Parameter
        
        
        ##### Training #####
        if self.isTrain:
            ## New Model Name
            self.modelName = 'nClass_%d_' % len(self.classNames)
            ## Corpus Path
            self.trainCorpusPath = "/Users/sephon/Desktop/Research/VizioMetrics/Corpus/VizSet_pm_ee_cat014_sub"
            ## Model Saving Path
            self.modelSavingPath = "/Users/sephon/Desktop/Research/VizioMetrics/Model"
            ## New Model Path
            self.modelPath = Common.getModelPath(self.modelSavingPath, self.modelName)
            
#         self.optSaveDst = '/Users/sephon/Desktop/Research/VizioMetrics/DB/'
        
        ##### Testing ######
        if self.isTest:
            ## Model ID
            self.modelName = 'nClass_7_2014-10-16_full'
            ## Model Saving Path
            self.modelSavingPath = '/Users/sephon/Desktop/Research/VizioMetrics/Model'
            ## Corpus Path
            self.testCorpusPath = "/Users/sephon/Desktop/Research/VizioMetrics/Corpus/VizSet_pm_ee_cat014_test"
            ## Default Dictionary Path
            self.dicPath = '/Users/sephon/Desktop/Research/VizioMetrics/Model/nClass_7_2014-10-16_full/'
            ## Default SVM Model Path
            self.svmModelPath = os.path.join(self.modelSavingPath, self.modelName)
            ## Result Directory
            self.resultSavingPath = '/Users/sephon/Desktop/Research/VizioMetrics/class_result'
            self.resultPath  = Common.getModelPath(self.resultSavingPath, self.modelName)
        
        
        ##### Testing/Classifying #####
        if self.isClassify:
            ## Model ID
            self.modelName = 'nClass_7_2014-10-14_1'
            ## Model Saving Path
            self.modelSavingPath = '/Users/sephon/Desktop/Research/VizioMetrics/Model'
            ## Corpus Path
            self.classifyCorpusPath = '/Users/sephon/Desktop/Research/VizioMetrics/Corpus/testCorpus'
            ## Default Dictionary Path
            self.dicPath = '/Users/sephon/Desktop/Research/VizioMetrics/Model/nClass_7_2014-10-14_1/'
            ## Default SVM Model Path
            self.svmModelPath = os.path.join(self.modelSavingPath, self.modelName)
            ## Result Directory
            self.resultSavingPath = '/Users/sephon/Desktop/Research/VizioMetrics/class_result'
            self.resultPath  = Common.getModelPath(self.resultSavingPath, '')
            
        print 'Options set!\n'

            
    def saveSetting(self, outPath = None):
        if outPath is None:
            outPath = self.modelPath
        
        print 'Saving options'
        classData = {}
        for i in range(0, len(self.classNames)):
            classData[i+1] = self.classNames[i]
        
        outPath = os.path.join(outPath, 'opt.pkl')   
        with open(outPath, 'wb') as fp:
            pickle.dump(classData, fp)
        print 'Options were saved in', outPath, '\n'
        
class Common():
    
    @staticmethod
    def makeDir(dst, dirName):
        path = os.path.join(dst, dirName)        
        try:
            os.makedirs(path)
            print "Create new directory " + path
            return path    
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                print  path + ' is existed.'
                pass
            else: raise
            return path
        
    @staticmethod
    def getModelPath(path, dirName):
        print dirName
        dirName = dirName + datetime.datetime.now().strftime("%Y-%m-%d")
        print dirName
        return Common.makeDir(path, dirName)
    
    
    @staticmethod
    def getFileNameAndSuffix(filePath):
        filename = filePath.split('/')[-1]
        suffix = filename.split('.')[1]
        return filename, suffix
    
        # File format: paper_id_image_id.{png, jpg,....}
    @ staticmethod
    def getIDsFromFilename(filename):
        filename = filename.split('.')
        filename = filename[0].split('_')
        return filename[1], filename[3]
    
    @ staticmethod
    def saveCSV(path, filename, content = None, header = None, mode = 'wb', consoleOut = True):

        if consoleOut:
            print 'Saving image information...'
        filePath = os.path.join(path, filename) + '.csv'
        with open(filePath, mode) as outcsv:
            writer = csv.writer(outcsv, dialect='excel')
            if header is not None:
                writer.writerow(header)
            if content is not None:
                for c in content:
                    writer.writerow(c)
        
        if consoleOut:  
            print filename, 'were saved in', filePath, '\n'
    