import os
import numpy as np
import pyrsgis as rg
from tensorflow import keras
from pyrsgis import raster
from pyrsgis.convert import changeDimension
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, precision_score, recall_score
from osgeo import gdal

def mainFunction(inputPath, outputPath):
    print('INPUT:', inputPath)
    print('OUTPUT:', outputPath)
    cwd = os.path.abspath(os.getcwd())
    mxBangalore = cwd + '\\' + 'l5_Bangalore2011_raw.tif'
    builtupBangalore = cwd + '\\' + 'l5_Bangalore2011_builtup.tif'
    mxtest = inputPath
   
    # Read the rasters as array
    ds1, featuresBangalore = raster.read(mxBangalore, bands=[1,2,3])
    ds2, labelBangalore = raster.read(builtupBangalore, bands=1)
    ds3, featurestest = raster.read(mxtest, bands='all')
    print(featuresBangalore.shape)
    print(featurestest.shape)
    # Print the size of the arrays
    print("Bangalore Multispectral image shape: ", featuresBangalore.shape)
    print("Bangalore Binary built-up image shape: ", labelBangalore.shape)
    print("Test Multispectral image shape: ", featurestest.shape)
    image = gdal.Open(mxBangalore)
     # Clean the labelled data to replace NoData values by zero
    labelBangalore = (labelBangalore == 1).astype(int)

    # Reshape the array to single dimensional array
    featuresBangalore = changeDimension(featuresBangalore)
    labelBangalore = changeDimension (labelBangalore)
    featurestest = changeDimension(featurestest)
    nBands = featuresBangalore.shape[1]
    
    print("Bangalore Multispectral image shape: ", featuresBangalore.shape)
    print("Bangalore Binary built-up image shape: ", labelBangalore.shape)
    print("Test Multispectral image shape: ", featurestest.shape)
    #.......................................Bandwise array extraction..................................................#
    inputfile = featuresBangalore
    NIR= inputfile[0]
    nir_flat=NIR.flatten().astype("Float32")
    green=inputfile[1]
    green_flat=green.flatten().astype("Float32")
    red =inputfile[2]
    red_flat=red.flatten().astype("Float32")
    label = labelBangalore

#.........................................brightness, NDVI,std, Variance...........................................................#

    brightness = (nir_flat+green_flat+red_flat)/3
    print("brightness is:",brightness)
    ndvi= np.nan_to_num((nir_flat-red_flat)/(nir_flat+red_flat))
    print("NDVI is:",ndvi)
    std=np.zeros(0)
    var=np.zeros(0)
    arr = np.zeros(0)
    pixel=NIR.flatten()
    for i in range(1,len(pixel)+1):
        print(i)

    for j in range(1,image.RasterCount+1):        
        arr= np.append(arr,(image.GetRasterBand(j).ReadAsArray().flatten())[i])
    std_arr=np.std(arr)
    std=np.append(std,std_arr)
    var_arr=np.var(arr)
    var=np.append(var,var_arr)
    arr = np.zeros(0)
    stacked_array = np.vstack(NIR.flatten(),green.flatten(),red.flatten(),ndvi.flatten(),var.flatten(),brightness.flatten(),label.flatten())
    array =np.transpose(stacked_array)
    

    #..................................Save the stacked array as .csv file for future use............................#    
    pd.DataFrame(array).to_csv("csvdata.csv")
    
    #.....................................Reading dataframe from csv.................................................#    
    dataset=pd.read_csv("csvdata.csv")
    path = mxtest
    featurestest = changeDimension(featurestest)
    
    #.................................defining X,y parameter for test_train_Split....................................#
    X = dataset.iloc[:,[1,2,3,4,5,6]]
    #X=dataset.iloc[:,:-1]  #entire dataframe except last column as last column of dataframe is of labels
    y = dataset.iloc[:,-1] # last column of labels only
    #y = labels.iloc[:,-1]
    
    #.....................................Running test_train_split...................................................#    
    X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.2,random_state=0) 
    print(X_train.shape)
    print(X_test.shape)
    print(y_train.shape)
    print(y_test.shape)
    #...................................designing random forest classifier...........................................#    
    classifier=RandomForestClassifier(n_jobs=2,random_state=0)
    classifier.fit(X_train,y_train)
    RandomForestClassifier(bootstrap=True, class_weight=None, criterion='gini', 
                            max_depth=None, max_features='auto', max_leaf_nodes=None,
                            min_impurity_split=1e-07, min_samples_leaf=1, min_samples_split=2, 
                            min_weight_fraction_leaf=0.0, n_estimators=100, n_jobs=2, oob_score=False,
                            random_state=0, verbose=0, warm_start=False) 
    
    #...................................predicting the output for the test data and calculating accuracy............#    
    preds = classifier.predict(X) 
    print("Accuracy:",metrics.accuracy_score(y, preds))
     #..................................predicting a new  image......................................................#    
    #predict_test_image = classifier.predict(featuresHyderabad)
    #.......................................function to convert array to image......................................#
    # def array_to_image(array,dtype,outfile):  
    #     image=gdal.Open(path)     
    #     trans = image.GetGeoTransform()
    #     proj = image.GetProjection()
    #     #nodata= image.GetRasterBand(1).GetNoDataValue()
    #     #out ="testimage.tif"
    #     outdriver = gdal.GetDriverByName("GTIFF")
    #     outdata = outdriver.Create(str(outfile),image.RasterXSize, image.RasterYSize, 1,gdal.GDT_Float32)
    #     outdata.GetRasterBand(1).WriteArray(array)
    #     #outdata.GetRasterBand(1).SetNoDataValue(nodata)
    #     outdata.SetGeoTransform(trans)
    #     outdata.SetProjection(proj)
    #     outdata=None
    
    # #.....convert back the predicted output array to image to check accuracy between labeled and predicted images....#    
    # prediction = np.reshape(predict_test_image, (ds3.RasterYSize, ds3.RasterXSize))
    # outpath = outputPath2
    # array_to_image(array=prediction,dtype="float64",outfile=outpath)
    return(0)

