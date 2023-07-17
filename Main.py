import numpy as np
import Import_And_Curate_Data as IACD
import Compute_Chi as Chi
import argparse
import matplotlib.pyplot as plt
from tkinter import Tk, Button


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('inputs', nargs='+', help='Input files or ranges')

    args = parser.parse_args()
    list_of_stiffnesses,list_of_amplitude,list_of_frequency,list_of_phase,list_of_data_frames = IACD.get_data_frames_from_list_of_names(args.inputs)
    R = 10**-6 # m
    eta = 10**-3  #Pa.s
    xi = 6 * np.pi * eta * R
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
    systems[-1].select_range()
    #def Compute_chi_omega():
    chi_omega = np.zeros((systems.__len__(),3),dtype=float)
    for n,system in enumerate(systems):
        system.make_fit()
        system.compute_chi()
        print([system.freq,system.chi.real,system.chi.imag])
        chi_omega[n] = [system.freq,system.chi.real,system.chi.imag]
    np.savetxt(chi_omega,"output.csv")
    #root = Tk()
    #root.mainloop()

