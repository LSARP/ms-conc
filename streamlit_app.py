from ms_conc import calibration_curves as cc
from ms_conc import ConcentrationEstimator as CE
from ms_conc import AppState as AS
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

def goodfit(x):
    if x > 3:
        return 'valid'
    return 'fail'

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


def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href


# st.write("a logo and text next to eachother")
# col1, mid, col2 = st.columns([10,1,25])
col1, mid, col2 = st.columns([10,1,25])
with col1:
    st.image('logo.png', width=140)
with col2:
    st.write('# An APP for computing concentrations using standard curves. V1.0.0')

    
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

url = "https://github.com/LewisResearchGroup/ms-conc"
st.write("check out this [link](%s) for the source code " % url)   
display_button()

def download_tutorial():
    display_instructions = st.selectbox('''or download the tutorial for better explanation''' , ('Close', 'download tutorial'))
    if display_instructions == 'download tutorial':
        st.write(get_binary_file_downloader_html('sample_files/SCALiR Tutorial.pdf', 'Tutorial.pdf'), unsafe_allow_html=True)

        
download_tutorial()
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
                                  'Click here to download an example of the standards concentrations file')
st.sidebar.write(tmp_download_link, unsafe_allow_html=True)

# st.sidebar.write("a sample file can be found [here](https://github.com/LSARP/ms-conc/tree/main/sample_files)")

std_info = st.sidebar.file_uploader('Upload standards concentrations file')
    

try:
#     if 'std_information' not in st.session_state:
    if True: # by doing this is possible to change the information file during execution
        st.session_state.std_information = pd.read_csv(std_info)
        if 'unit' in st.session_state.std_information.columns:
            st.session_state.units = st.session_state.std_information[['peak_label','unit']].fillna('')
            st.session_state.std_information = st.session_state.std_information.drop(columns = ['unit'])
        else:
            st.write("missing units column in the standard information table")

        if 'internal_standard' in st.session_state.std_information.columns:
            st.session_state.internal_standard = st.session_state.std_information[['peak_label','internal_standard']]
            st.session_state.internal = 'on'
            
            st.write("the calculations will proceed according to internal standards protocol")
        else:
            st.session_state.internal = 'off'
            
    st.write('## Your standards concentrations file:')
    st.write(st.session_state.std_information)
except:
    st.write('## Please upload your standards concentrations file to start')
    
    
st.sidebar.write('## 2) Please upload the peaklist data file. Data from Maven or Mint are accepted.\
                 Data files may be in .csv or .xlsx format.')
# st.sidebar.write("a sample file can be found [here](https://github.com/LSARP/ms-conc/tree/main/sample_files)")

tmp_download_link = download_link(pd.read_csv('sample_files/SCALiR_MINT_Peaklist_Dense_Peak_Max.csv'), 
                                  'SCALiR_MINT_Peaklist_Dense_Peak_Max_sample.csv', 
                                  'Click here to download an example of the Mint dense peaklist file')
st.sidebar.write(tmp_download_link, unsafe_allow_html=True)

tmp_download_link = download_link(pd.read_csv('sample_files/SCALiR_MINT_Peaklist_Full_Results.csv'), 
                                  'SCALiR_MINT_Peaklist_Full_Results_sample.csv', 
                                  'Click here to download an example of the Mint full peaklist file')
st.sidebar.write(tmp_download_link, unsafe_allow_html=True)
            
tmp_download_link = download_link(pd.read_csv('sample_files/SCALiR_Maven_Peaklist.csv'), 
                                  'SCALiR_Maven_Peaklist_sample.csv', 
                                  'Click here to download an example of the Maven peaklist file')
st.sidebar.write(tmp_download_link, unsafe_allow_html=True)

results_file = st.sidebar.file_uploader("upload the data file..")

try:
#     if 'raw_results' not in st.session_state:
    if True: # by doing this is possible to change the results file during execution
        if '.csv' in results_file.name:
            st.session_state.raw_results = pd.read_csv(results_file)
            st.session_state.raw_results = st.session_state.raw_results.dropna(thresh = 1, axis = 0)
        if '.xlsx' in results_file.name:
            st.session_state.raw_results = pd.read_excel(results_file)
            st.session_state.raw_results = st.session_state.raw_results.dropna(thresh = 1, axis = 0)
            
        st.write('## Your peaklist data file:')
        st.write(st.session_state.raw_results)
        try:
            if st.session_state.internal == 'off': 
                st.session_state.program = st.selectbox('''Select the program used for generating the peaklist data''' , ('Mint', 'Maven'))
            #     st.write('you selected ' + st.session_state.program + ' program')
                if st.session_state.program == 'Mint':
                    st.session_state.mint_table_type = st.selectbox('''Indicate the type of table used, see Mint documentation for details''', ('full results', 'dense peak_max'))
                    
                    if st.session_state.mint_table_type == 'full results':
                        st.write('''Please select the intensity measurement..
                                peak_max will be used as the default value''')
                        try:
                            st.session_state.by_ = st.selectbox('intensity measurement',('peak_max', 'peak_area'))
                        except:
                            st.session_state.by_ = 'peak_max'
                        st.session_state.raw_results = cc.info_from_Mint(st.session_state.raw_results, st.session_state.by_)
                            
                    if st.session_state.mint_table_type == 'dense peak_max':          
                        st.session_state.raw_results = cc.info_from_Mint_dense(st.session_state.raw_results)
                       #  st.write(st.session_state.raw_results)
                        
                        st.session_state.by_ = 'peak_max'
                         
                if st.session_state.program == 'Maven':
                    st.session_state.by_ = 'value'
                    st.session_state.raw_results = cc.info_from_Maven(st.session_state.raw_results)
            #         st.write(st.session_state.raw_results)
            if st.session_state.internal == 'on':
                # Internal standards will use the same table format as mint dense
                st.session_state.raw_results = cc.info_from_Mint_dense(st.session_state.raw_results)

            
            st.session_state.output = st.session_state.raw_results.copy()
            st.session_state.output['STD_CONC'] = np.nan
            if set(np.unique(st.session_state.raw_results.peak_label)) != set(np.unique(st.session_state.std_information.peak_label)):
                    st.write('ALERT!')
                    st.write('Some compounds in the peaklist file were not found in the standards concentrations file. Only compounds in the standards concentrations file will be quantified.')
                    st.session_state.intercept = np.intersect1d( np.unique(st.session_state.raw_results.peak_label), np.unique(st.session_state.std_information.peak_label) )
                    st.session_state.raw_results = st.session_state.raw_results[st.session_state.raw_results.peak_label.isin( st.session_state.intercept )]
                    st.session_state.std_information = st.session_state.std_information[st.session_state.std_information.peak_label.isin( st.session_state.intercept )]
        
            st.session_state.std_results = cc.setting_from_stdinfo(st.session_state.std_information, st.session_state.raw_results)
            st.session_state.std_results.sort_values(by = ['peak_label','STD_CONC', st.session_state.by_ ], inplace = True)
        #     st.write('here i am')
            
        except:
            st.write('## Data uploading or parameter settings incomplete')

        
except:
    st.write('## No peaklist datafile has been uploaded')
    


try:
    if len(st.session_state.std_results) > 1:
#         st.write('here i am')
        
        st.session_state.fl = st.selectbox('''Select the flexibility for your line of best fit\n''' , 
                               ('Fixed fit – the app will only generate a standard curve with a slope = 1.00', 
                                'Interval fit – bounds for slope values can be defined. The interval 0.85-1.15 is recommended',
                                'Wide fit – the app will not constrain the slope when calculating the line of best fit',))
        
        st.session_state.fl = st.session_state.fl.split(' ')[0].lower()
        st.write(st.session_state.fl)
        
        st.session_state.ces = CE.ConcentrationEstimator()
        
        if st.session_state.fl == 'interval':
            st.session_state.interval = st.slider('Select a range of values', 0.0, 2.0, (0.85, 1.15))
            st.session_state.ces.set_interval(np.array(st.session_state.interval))
            st.write(st.session_state.ces.interval)
        
        st.session_state.x_train, st.session_state.y_train = cc.training_from_standard_results(st.session_state.std_results, by = st.session_state.by_)
        
        st.session_state.ces.fit(st.session_state.x_train, st.session_state.y_train, v_slope = st.session_state.fl)
        
        st.write('''The standard curves have been fitted.
             You can download the parameters of the standard curves.''')
        
        
        st.session_state.linear_scale_parameters = st.session_state.ces.params_.sort_values(by = ['peak_label']).drop(['lin_range_min', 'lin_range_max'], axis = 1)
        st.session_state.linear_scale_parameters = st.session_state.ces.params_.sort_values(by = ['peak_label']).drop(['lin_range_min', 'lin_range_max'], axis = 1)

        st.session_state.linear_scale_parameters.rename(columns = {'slope':'log_scale_slope', 'intercept':'log_scale_intercept'}, inplace = True)
        
        st.session_state.linear_scale_parameters['log_scale_slope'] = 1/st.session_state.linear_scale_parameters.log_scale_slope
        st.session_state.linear_scale_parameters['log_scale_intercept'] = \
                                    -st.session_state.linear_scale_parameters.log_scale_intercept*st.session_state.linear_scale_parameters.log_scale_slope
        
        st.session_state.linear_scale_parameters['Valid_fit'] = st.session_state.linear_scale_parameters.N_points.apply(lambda x: goodfit(x))
        
        st.write(st.session_state.linear_scale_parameters)
        
        st.write('''Interpretation of columns in the standard curve parameters file: \n
        peak_label: name of compound\n
        log_scale_slope: value of the slope in the natural log (ln) scale with concentration in the X axis (note, for the fixed slope option the slope always = 1)\n
        log_scale_intercept: value of the intercept in the natural log (ln) scale with concentration in the X axis\n
 
        N_points: number of points in the standard curve (curves with < 5 points are semi-quantitative)\n
        Residual: measurement of goodness of fit for the standard curve (residual value < 0.01 indicates a high quality fit)\n
        LLOQ: lower limit of quantification\n
        ULOQ: upper limit of quantification\n
        Valid_fit: when the number of points in the linear fit is lower than 4 the fitting is considered failed
        ''')
        
        tmp_download_link = download_link(st.session_state.linear_scale_parameters, 'parameters.csv', 'Click here to download your standard curve parameters')
        st.markdown(tmp_download_link, unsafe_allow_html=True)
            
        
        st.session_state.X = st.session_state.raw_results[['ms_file','peak_label', st.session_state.by_]].rename(columns={st.session_state.by_:'value'})
        
        st.session_state.tr = st.session_state.ces.predict(st.session_state.X)
        st.session_state.X['pred_conc'] = st.session_state.tr.pred_conc
        st.session_state.X['in_range'] = st.session_state.tr.in_range

        st.write(st.session_state.X)
        st.write('''Interpretation of columns in the concentration data file: \n
        ms_file: name of sample\n
        peak_label: name of compound\n
        value: signal intensity value for sample in peaklist datafile\n
        pred_conc: concentration value calculated by SCALiR\n
        in_range: 1 = concentration is within the linear range; 0 = concentration is NOT within the linear range\n
        *Note: concentrations outside the linear range are not considered quantitative
        ''')        
        
        tmp_download_link = download_link(st.session_state.X, 'results.csv', 'Click here to download your concentration data')
        st.markdown(tmp_download_link, unsafe_allow_html=True)
        
        try:
            st.write('''Log-log plot visualization: \n
            Description: This plot shows the x- and y-axes in the log scale, with the axis tick labels in the linear scale
                ''')        
        
            st.session_state.cp = st.selectbox('select the compound \n' + 
                                   st.session_state.x_train.peak_label.iloc[0] +
                                   ' will be used by default', list(np.unique(st.session_state.x_train.peak_label)))
            st.write(st.session_state.cp)
        
        
        #### making the figure #####
                
            y_train_corrected = cc.train_to_validation(st.session_state.x_train, st.session_state.y_train, st.session_state.ces.params_ )
            x_viz = st.session_state.x_train.copy()
        
            x_viz['pred_conc'] = st.session_state.ces.predict(x_viz).pred_conc
                
                
            x_viz['Concentration'] = st.session_state.y_train
                
            
            x_viz['Corr_Concentration'] = y_train_corrected
            
            x_viz = x_viz.fillna(-1.0)
            
            x_viz['in_range'] = x_viz.Corr_Concentration.apply(lambda x: heav(x))
            x_viz = x_viz[x_viz.Concentration > 0.00000001]
                
            dat = x_viz[x_viz.peak_label == st.session_state.cp]
            dat = dat[dat.value > 0]
            st.write(dat[dat.columns[:-2]])
            st.session_state.u = st.session_state.units.unit[st.session_state.units.peak_label == st.session_state.cp].iloc[0]
            st.session_state.xlabel = st.text_input("Please enter the x-label", st.session_state.cp + ' concentration (' + st.session_state.u + ')')
            st.session_state.ylabel = st.text_input("Please enter the y-label", st.session_state.cp + ' intensity (AU)')
        
        
            
            fig = plt.figure(figsize = (4,4))
            for inr, colo in zip( [2, 1]   , ['gray', 'black']):
                plt.plot(np.array(dat.Concentration)[dat.in_range == inr], np.array(dat.value)[dat.in_range == inr], 'o', color = colo)
                       
            plt.plot(np.array(dat.pred_conc)[dat.in_range == 1] , np.array(dat.value)[dat.in_range == 1] , color = 'black')
            
            plt.xlabel(st.session_state.xlabel, fontsize = 14)
            plt.ylabel(st.session_state.ylabel, fontsize = 14)
            plt.xscale('log')
            plt.yscale('log')
                
            st.pyplot(fig, dpi = 1000)             
        
        
        
        except:
            st.write('')
except:
    st.write('## There are no results to show')
    


    

