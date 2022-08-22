from ms_mint_conc import calibration_curves as cc
from ms_mint_conc import ConcentrationEstimator as CE
from ms_mint_conc import AppState as AS
from ms_mint_conc import SessionState
from ms_mint_conc.SessionState import get
import matplotlib.pyplot as plt
import os
import pandas as pd
import datetime
import numpy as np
import glob
import re

import streamlit as st
import base64
from io import BytesIO


def heav(x):
    if x > 0.0:
        return 1
    return 2

def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

# st.write("a logo and text next to eachother")
# col1, mid, col2 = st.columns([10,1,25])
col1, mid, col2 = st.beta_columns([10,1,25])
with col1:
    st.image('logo.png', width=140)
with col2:
    st.write('# An APP for computing concentrations using standard curves')
    
def display_button():
    display_instructions = st.selectbox('''Click here to see instructions''' , ('Close', 'Show Instructions'))
    if display_instructions == 'Show Instructions':
        st.markdown("""
         #### This app can process both Mint and Maven peaklist datasets.\n
         #####    1) A table with the concentrations of standard samples (metadata) is required. Upload by clicking the button on the left. Follow the link to find a standards concentrations file template.\n
         #####    2) Next, upload the peaklist data file from Mint or Maven.  You may upload the full results or dense peak max data file generated from Mint. You do not have to remove or re-arrange any columns generated by these programs before uploading. Follow the links to find peaklist file templates.
         ######     The standards concentrations table should contain the file names of standards as column names.
         ######     The first column of the standards concentrations file corresponds to the Compound ID or peak labels for the metabolites in the standards.
         ######     Please make sure that the file names for standards and compound names in the standards concentrations file and peaklist data file are the same.
         """)
        st.write('''         
         #####    3) When the standards concentrations file and peaklist data files are uploaded, a table with the parameters of the standard curves will be generated automatically and includes:
         ###### Peak_label\n
         ###### Log_scale_slope\n
         ###### Log_scale_intercept\n
         ###### N_points (number of points in the linear range)\n
         ###### Residual (a magnitude for computing the difference between the estimated and real concentrations in the linear range)\n
         ###### LLOQ (lower limit of quantification)\n
         ###### ULOQ (upper limit of quantification)\n
         #####    4) In the case that Mint was used to generate the peaklist data file, a selection tab will pop up for selecting the parameter for the peak intensity measurement; peak_max is the default value
         #####    5) At the bottom of this page, you can visualize the standard curves and the linear ranges predicted for each compound (shown in black). Concentrations outside the linear range are shown in grey.    
         #####    6) A table with the predicted concentrations for each compound will be generated automatically and includes:
         ###### Ms_file (file name) 
         ###### Peak_label (compound name)
         ###### Value (signal intensity values inputted by the user)
         ###### Pred_conc (concentration of compound predicted from the standard curve equation)
         ###### In_range (1 = the concentration is in the linear range and 0 = the concentration is NOT in the linear range)
         ###### *Note: Concentrations outside the linear range should not be considered quantitative.
         ''')
        
display_button()
#st.markdown("""
         #### This app can process both MINT and MAVEN result datasets.\n
         #####    1) A table with the concentrations of standard samples (metadata) is required. Upload by clicking the button on the left. Follow the link to find a standards concentrations file template.\n
         #####    2) Next, upload the data file from MINT or Maven.  You may upload the full results or dense peak max data file generated from MINT. You do not have to remove or re-arrange any columns generated by these programs before uploading. Follow the links to find data file templates.
         ######     The standards concentration table should contain the file names of standard samples as column names (without the file extension).
         ######     The first column of the standards concentration file corresponds to the Compound ID or peak labels for the metabolites in the standard samples.
         ######     Please make sure that the file names for standards and compound names in the standards concentration file and data file are the same. Remove any compounds that are not in both the standards concentration file and data file.
#         """)

#st.image('picture_4_app.png', width=700, caption = 'Figure 1. Example of a standards concentration file. The file names for the standards should be contained in the column names. The column ‘peak_label’ (MINT) or compoundId (Maven) corresponds to the compounds in the standard samples.')

# st.write('''         
#          #####    3) When the standards concentrations file and data files are uploaded, a table with the parameters of the standard curves (slope, intercept, upper limit of quantification, lower limit of quantification) will be generated automatically and includes:
#          ###### Peak_label\n
#          ###### Log_scale_slope\n
#          ###### Log_scale_intercept\n
#          ###### N_points (number of points in the linear range)\n
#          ###### Residual (a magnitude for compute the difference between the estimated and real concentrations in the linear range)\n
#          ###### LLOQ (lower limit of quantification)\n
#          ###### ULOQ (upper limit of quantification\n
#          #####    4) In the case that Mint program is used to generate the results, a selection tab will pop up for selecting the parameter for the peak intensity measurement, peak_max is the defalult value
#          #####    5) At the bottom of this page, you can visualize the standard curves and the linear ranges predicted for each compound (black dots)    
#          #####    6) A table with the predicted concentrations for each compound will be generated automatically and includes:
#          ###### Ms_file 
#          ###### Peak_label
#          ###### Value (signal intensity values inputted by the user)
#          ###### Pred_conc (concentration of compound predicted from the standard curve equation)
#          ###### In_range (1 = the concentration is in the linear range and 0 = the concentration is NOT in the linear range)
#          ###### *Note: Concentrations outside the linear range should not be considered quantitative.
#          ''')
# state = AS.AppState()
st.sidebar.write( '## 1) Please upload standards concentrations file' )

tmp_download_link = download_link(pd.read_csv('sample_files/SCALiR_Standards_Concentrations File.csv'), 'SCALiR_Standards_Concentrations_sample.csv', 
                                  'click here to download an example of standard concentration file')
st.sidebar.write(tmp_download_link, unsafe_allow_html=True)

# st.sidebar.write("a sample file can be found [here](https://github.com/LSARP/ms-conc/tree/main/sample_files)")

std_info = st.sidebar.file_uploader('Upload standards concentrations file')

# try:
#     print(std_info)
# except:
#     print('no detected info file')



try:
    s_st = SessionState.get(std_information = pd.read_csv(std_info))
    st.write('## Your standards concentrations file:')
    st.write(s_st.std_information)
except:
    st.write('## Please upload your standards concentrations file to start')
    
    
st.sidebar.write('## 2) Please upload the peaklist data file. Data from Maven or Mint are accepted.\
                 Data files may be in .csv or .xlsx format.')
# st.sidebar.write("a sample file can be found [here](https://github.com/LSARP/ms-conc/tree/main/sample_files)")
tmp_download_link = download_link(pd.read_csv('sample_files/SCALiR_MINT_Peaklist_Dense_Peak_Max.csv'), 
                                  'MINT_Peaklist_Dense_Peak_Max_sample.csv', 
                                  'click here to download an example of Mint Dense results file')
st.sidebar.write(tmp_download_link, unsafe_allow_html=True)

tmp_download_link = download_link(pd.read_csv('sample_files/SCALiR_MINT_Peaklist_Full_Results.csv'), 
                                  'SCALiR_MINT_Peaklist_Full_Results_sample.csv', 
                                  'click here to download an example of Mint Full results file')
st.sidebar.write(tmp_download_link, unsafe_allow_html=True)
            
tmp_download_link = download_link(pd.read_csv('sample_files/SCALiR_Maven_Peaklist.csv'), 
                                  'SCALiR_Maven_Peaklist.csv', 
                                  'click here to download an example of Maven results file')
st.sidebar.write(tmp_download_link, unsafe_allow_html=True)

results_file = st.sidebar.file_uploader("upload the data file..")

try:
    if '.csv' in results_file.name:
        s_st.raw_results = pd.read_csv(results_file)
    if '.xlsx' in results_file.name:
        s_st.raw_results = pd.read_excel(results_file)
        
    st.write('## Your peaklist data file:')
    st.write(s_st.raw_results)
except:
    st.write('## No peaklist datafile has been uploaded')
    
try:
    s_st.program = st.selectbox('''Select the program used for generating the peaklist data''' , ('Mint', 'Maven'))
    
    if s_st.program == 'Mint':
        s_st.mint_table_type = st.selectbox('''Indicate the type of table used, see Mint documentation for details''', ('full results', 'dense peak_max'))
        
        if s_st.mint_table_type == 'full results':
            st.write('''Please select the intensity measurement..
                    peak_max will be used as the default value''')
            try:
                s_st.by_ = st.selectbox('intensity measurement',('peak_max', 'peak_area'))
            except:
                s_st.by_ = 'peak_max'
#             s_st.raw_results = cc.info_from_Mint(s_st.raw_results)
                
        if s_st.mint_table_type == 'dense peak_max':          
            s_st.raw_results = cc.info_from_Mint_dense(s_st.raw_results)
            st.write(s_st.raw_results)
            
            s_st.by_ = 'peak_max'
             
    if s_st.program == 'Maven':
        s_st.by_ = 'value'
        s_st.raw_results = cc.info_from_Maven(s_st.raw_results)
        
    s_st.output = s_st.raw_results.copy()
    s_st.output['STD_CONC'] = np.nan
    
# # #     st.write(s_st.std_information)
# #     for file in np.unique(s_st.output.ms_file):
# #         for cp in np.unique(s_st.output.peak_label):
# #             try:
# # #                 st.write(file)
# #                 st.write( s_st.std_information[file].iloc[0] )
                
# #                 s_st.output.STD_CONC[(s_st.output.ms_file == file) & (s_st.output.peak_label == cp)] = \
# #                 s_st.std_information[file][s_st.std_information.peak_label == cp].iloc[0]
# #                 st.write(file)
# #             except:
# #                 continue
    
    
# #     st.write(s_st.raw_results)
    s_st.std_results = cc.setting_from_stdinfo(s_st.std_information, s_st.raw_results)
#     st.write(s_st.std_results)
    s_st.std_results.sort_values(by = ['peak_label','STD_CONC', s_st.by_ ], inplace = True)
#     st.write('here i am')
    
except:
    st.write('## Data uploading or parameter settings not complete')


try:
#     st.write(len(s_st.std_results))
    if len(s_st.std_results) > 1:
#         st.write('here i am')
        
        s_st.fl = st.selectbox('''Select the flexibility for your line of best fit\n''' , 
                               ('Fixed fit – the app will only generate a standard curve with a slope = 1.00', 
                                'Interval fit – bounds for slope values can be defined. The interval 0.85-1.15 is recommended',
                                'Wide fit – the app will not constrain the slope when calculating the line of best fit',))
        
        s_st.fl = s_st.fl.split(' ')[0].lower()
        st.write(s_st.fl)
        
        s_st.ces = CE.ConcentrationEstimator()
        
        if s_st.fl == 'interval':
            s_st.interval = st.slider('Select a range of values', 0.0, 2.0, (0.85, 1.15))
#             st.write('interval: ', s_st.interval[0])
            s_st.ces.set_interval(np.array(s_st.interval))
            st.write(s_st.ces.interval)
        
        s_st.x_train, s_st.y_train = cc.training_from_standard_results(s_st.std_results, by = s_st.by_)
        
        s_st.ces.fit(s_st.x_train, s_st.y_train, v_slope = s_st.fl)
        
#         st.write(s_st.ces.params_)
        st.write('''The standard curves have been fitted.
             You can download the parameters of the standard curves.''')
        
        
        s_st.linear_scale_parameters = s_st.ces.params_.sort_values(by = ['peak_label']).drop(['lin_range_min', 'lin_range_max'], axis = 1)

        s_st.linear_scale_parameters.rename(columns = {'slope':'log_scale_slope', 'intercept':'log_scale_intercept'}, inplace = True)
#         s_st.linear_scale_parameters.rename(columns={})
        st.write(s_st.linear_scale_parameters)
    
        st.write('''the standard curves have being fitted ....
             you can download the parameters of the standard curves....''')
        
        tmp_download_link = download_link(s_st.linear_scale_parameters, 'parameters.csv', 'Click here to download your standard curve parameters')
        st.markdown(tmp_download_link, unsafe_allow_html=True)
            
        
        s_st.X = s_st.raw_results[['ms_file','peak_label', s_st.by_]].rename(columns={s_st.by_:'value'})
#         st.write(s_st.X)
#         st.write(s_st.ces.params_)
#         st.write(s_st.X)
        s_st.tr = s_st.ces.predict(s_st.X)
        s_st.X['pred_conc'] = s_st.tr.pred_conc
#         st.write(s_st.X)
        s_st.X['in_range'] = s_st.tr.in_range
#     st.write(s_st.X)
#         X['pred_conc'] = ces.predict(X).pred_conc
        st.write(s_st.X)
        tmp_download_link = download_link(s_st.X, 'results.csv', 'Click here to download your concentration data')
        st.markdown(tmp_download_link, unsafe_allow_html=True)
        
except:
    st.write('## There are no results to show')
    

try:
    s_st.cp = st.selectbox('select the compound \n' + 
                           s_st.x_train.peak_label.iloc[0] +
                           ' will be used by default', list(np.unique(s_st.x_train.peak_label)))
    st.write(s_st.cp)



        
    y_train_corrected = cc.train_to_validation(s_st.x_train, s_st.y_train, s_st.ces.params_ )
    x_viz = s_st.x_train.copy()

    x_viz['pred_conc'] = s_st.ces.predict(x_viz).pred_conc
        
        
    x_viz['Concentration'] = s_st.y_train
        
    
    x_viz['Corr_Concentration'] = y_train_corrected
    
    x_viz = x_viz.fillna(-1.0)
    
    x_viz['in_range'] = x_viz.Corr_Concentration.apply(lambda x: heav(x))
    x_viz = x_viz[x_viz.Concentration > 0.00000001]
        
    dat = x_viz[x_viz.peak_label == s_st.cp]
    dat = dat[dat.value > 0]
    st.write(dat)
    
    s_st.xlabel = st.text_input("Please enter the x-label", s_st.cp + ' concentration (μM)')
    s_st.ylabel = st.text_input("Please enter the y-label", s_st.cp + ' intensity (AU)')
               
#     s_st.viz_restult = st.button('''plot results''')
#     if s_st.viz_restult:        
    fig = plt.figure(figsize = (4,4))
    for inr, colo in zip( [2, 1]   , ['gray', 'black']):
        plt.plot(dat.Concentration[dat.in_range == inr], dat.value[dat.in_range == inr], 'o', color = colo)
               
    plt.plot(dat.pred_conc[dat.in_range == 1] , dat.value[dat.in_range == 1] , color = 'black')
    
    plt.xlabel(s_st.xlabel, fontsize = 14)
    plt.ylabel(s_st.ylabel, fontsize = 14)
    plt.xscale('log')
    plt.yscale('log')
        
    st.pyplot(fig, dpi = 1000)

except:
    st.write('')
    
    
