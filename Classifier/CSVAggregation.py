# Modify .csv files that has "[ ]"

import os, errno, csv
import locale


def read_float_with_comma(num):
    return locale.atof(num)
 
csv_path = '/Users/sephon/Desktop/Research/VizioMetrics/cloud_result/class_result_5cat_0313/'
resultCSVList = []
errorCSVList = []
invalidCSVList = []
 
for dirPath, dirNames, fileNames in os.walk(os.path.join(csv_path, 'fromEC2')):   
            for f in fileNames:
                suffix = f.split('.')[1]
                if suffix == 'csv':
#                     print f.split('_')
                    print f
                    type = f.split('_')[1]
                    if type == 'class':
                        resultCSVList.append(os.path.join(dirPath, f))
                    elif type == 'error':
                        errorCSVList.append(os.path.join(dirPath, f))
                    elif type == 'invalid':
                        invalidCSVList.append(os.path.join(dirPath, f))
                         
print resultCSVList
print errorCSVList
print invalidCSVList

finalClassFile = os.path.join(csv_path, 'final5catClass.csv')
finalErrorFile = os.path.join(csv_path, 'final5catError.csv')
finalInvalidFile = os.path.join(csv_path, 'final5catInvalid.csv')
count_classFile = 0
count_errorFile = 0
count_invalidFile = 0
# a = "6.52353753563e-7"
# print float(a)
 
  
with open(finalClassFile, 'wb') as outcsv:
    writer = csv.writer(outcsv, dialect='excel')
    header = ['img_id', 'pmcid', 'img_loc', 'class_name', 'class_probability', 'img_format', 'img_height', 'img_width', 'key_size']
    writer.writerow(header)
    for f in resultCSVList:
        print 'converting %s...' %f
        with open(f ,'rb') as incsv:
            reader = csv.reader(incsv, dialect='excel')
            reader.next()
            for row in reader:
                count_classFile += 0
                
                image_id = row[0].split('/')[-1]
                img_loc = os.path.join('pubmed/img', image_id)
                pmcid = image_id.split('_')[0][3:]
#                 paper_id = image_id.split('_')[0]
#                 classname = row[1]
#                 classname = classname[2:-2]
#                 prob = row[2]
#                 prob = prob[3:-3].split()
#                 print prob
#                 prob = map(float, prob)
                classname, prob, format, img_h, img_w, img_size = row[1:]
                
                newRow = [image_id, pmcid, img_loc, classname, prob, format, img_h, img_w, img_size]
#                 print newRow
                writer.writerow(newRow)
                 
         
# with open(finalErrorFile, 'wb') as outcsv:
#     writer = csv.writer(outcsv, dialect='excel')
#     header = ['image_id', 'image_location', 'file_size']
#     writer.writerow(header)
#     for f in errorCSVList:
#         print 'converting %s...' %f
#         with open(f ,'rb') as incsv:
#             reader = csv.reader(incsv, dialect='excel')
#             reader.next()
#             for row in reader:
#                 fname = row[0]
#                 image_id = fname.split('/')[1]
#                 row.insert(0, image_id)
#                 writer.writerow(row)
#                 
# with open(finalInvalidFile, 'wb') as outcsv:
#     writer = csv.writer(outcsv, dialect='excel')
#     header = ['image_id', 'image_location', 'file_size']
#     writer.writerow(header)
#     for f in invalidCSVList:
#         print 'converting %s...' %f
#         with open(f ,'rb') as incsv:
#             reader = csv.reader(incsv, dialect='excel')
#             reader.next()
#             for row in reader:
#                 fname = row[0]
#                 image_id = fname.split('/')[1]
#                 row.insert(0, image_id)
#                 writer.writerow(row)
#              
# 
# finalClassFile = os.path.join(csv_path, 'conversion_5cat.csv')
# finalErrorFile = os.path.join(csv_path, 'conversionError_5cat.csv')
# count_classFile = 0
# count_errorFile = 0
#         
# with open(finalClassFile, 'wb') as outcsv:
#     writer = csv.writer(outcsv, dialect='excel')
#     header = ['image_location', 'is_convertable']
#     writer.writerow(header)
#     for f in resultCSVList:
#         print 'converting %s...' %f
#         with open(f ,'rb') as incsv:
#             reader = csv.reader(incsv, dialect='excel')
#             reader.next()
#             for row in reader:
#                 count_classFile += 0
#                 newRow = [row[0], 1]
#                 writer.writerow(newRow)
#                   
# with open(finalErrorFile, 'wb') as outcsv:
#     writer = csv.writer(outcsv, dialect='excel')
#     header = ['image_location', 'is_convertable']
#     writer.writerow(header)
#     for f in errorCSVList:
#         print 'converting %s...' %f
#         with open(f ,'rb') as incsv:
#             reader = csv.reader(incsv, dialect='excel')
#             reader.next()
#             for row in reader:
#                 newRow = [row[0], 0]
#                 writer.writerow(newRow)
        
     
             
# csv_path = '/Users/sephon/Desktop/Research/VizioMetrics/cloud_result/all_s3file/'
# finalClassFile = os.path.join(csv_path, 'finalClass.csv')
# finalErrorFile = os.path.join(csv_path, 'finalError.csv')
# count_classFile = 0
# count_errorFile = 0
# # a = "6.52353753563e-7"
# # print float(a)
# 
# print finalClassFile
# with open(finalClassFile, 'wb') as outcsv:
#     writer = csv.writer(outcsv, dialect='excel')
#     header = ['image_id', 'image_loc', 'file_format', 'file_size']
#     writer.writerow(header)
#     f = "/Users/sephon/Desktop/Research/VizioMetrics/cloud_result/all_s3file/s3_files.csv"
#     print 'converting %s...' %f
#     with open(f ,'rb') as incsv:
#         reader = csv.reader(incsv, dialect='excel')
#         reader.next()
#         for row in reader:
#             count_classFile += 0
#             fname = row[0]
#             image_id = fname.split('/')[1]
#             classname = row[1]
#             classname = classname[2:-2]
#             
#             newRow = [image_id, fname, row[1], row[2]]
#             writer.writerow(newRow)   
#         