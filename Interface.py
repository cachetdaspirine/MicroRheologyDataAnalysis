import numpy as np
import Import_And_Curate_Data as IACD
import Compute_Chi as Chi


def setup_systems(filenames,xi):
    list_of_stiffnesses,list_of_amplitude,list_of_frequency,list_of_phase,list_of_data_frames = IACD.get_data_frames_from_list_of_names(filenames)
    
    # This is used to extract the force along X
    # no matter what the names are column_names[0] is the force 1 [1] is the force 2, [2] is the time, [3] is the time within one serie
    column_names = ['xSignal1', 'xSignal2', 'time','seriesTime']
    for name in column_names:
        if name not in list_of_data_frames[0].columns :
            raise KeyError('Invalide column names : '+name+' does not exist. Please verify your input file, and modify the variable column_names accordingly.'
                                        +'The names of the columns are '+str(list_of_data_frames[0].columns))
    systems= list()
    for i in range(list_of_stiffnesses.__len__()):
        systems.append( Chi.setup(stiffnesses=list_of_stiffnesses[i],
                                            amplitude=list_of_amplitude[i],
                                            phase = list_of_phase[i],
                                            frequency = list_of_frequency[i],
                                            xi = xi,
                                            data_frame=list_of_data_frames[i],
                                            column_names = column_names))
    return systems

def  select_range(systems,ShowResults):
    for system in systems:
        system.select_range(ShowResults)

def compute_chi(systems,filename):
    chi_omega = np.zeros((systems.__len__(),3),dtype=float)
    for n,system in enumerate(systems):
        system.compute_chi()
        #print([system.freq,system.chi.real,system.chi.imag])
        chi_omega[n] = [system.freq,system.chi.real,system.chi.imag]
    np.savetxt(filename,chi_omega)

def fitting_parameters(systems,file=None):
    fitting_parameters = list()
    for system in systems:
        fitting_parameters.append(system.get_fitting_parameters())
    fitting_parameters = np.array(fitting_parameters)
    if file:
        np.save(file,fitting_parameters,allow_pickle=True)
    else:
        return fitting_parameters