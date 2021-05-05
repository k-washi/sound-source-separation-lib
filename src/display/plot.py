import matplotlib.pyplot as plt
import numpy as np
def plot_mic_locations(locations, epsilon=0.02):
    """
    locations: [2, ...]
    """
    plt.figure()
    g = plt.subplot()
    plt.title('Microphone locations')
    plt.scatter(locations[0], locations[1])

    loc_max = np.max(locations) + epsilon
    plt.xlim([-loc_max, loc_max])
    plt.ylim([-loc_max, loc_max])
    plt.xlabel("x[m]")
    plt.ylabel("y[m]")
    g.set_aspect('equal')

    plt.tight_layout()
    plt.show()

def plot_ss_locations(locations, epsilon=0.1):
    """
    locations: [2, ...]
    """
    plt.figure()
    g = plt.subplot()
    plt.title('virtual sound source locations')
    plt.scatter(locations[0], locations[1])

    loc_max = np.max(locations) + epsilon
    plt.xlim([-loc_max, loc_max])
    plt.ylim([-loc_max, loc_max])
    plt.xlabel("x[m]")
    plt.ylabel("y[m]")
    g.set_aspect('equal')
    plt.tight_layout()
    plt.show()

def plot_spectrogram(spectrogram, ss_dirs, time_stamps):
    """
    spectrogram: freqs, dirs, times
    """
    person_freq_min = 30
    person_freq_max = 100
    spectrogram = np.mean(spectrogram[person_freq_min:person_freq_max], axis=0)
    ss_dirs *= 180/np.pi
    plt.title("Spectrogram")
    #X, Y = np.meshgrid(time_stamps, ss_dirs)
    plot_s = np.clip(spectrogram, 2, 7.5)
    plt.pcolormesh(time_stamps, ss_dirs, plot_s)
    #plt.contourf(X, Y, spectrogram, cmap=plt.cm.bone)
    plt.xlabel("time [sec]")
    plt.ylabel("azimuth [deg]")
    plt.show()
    #plt.hist(spectrogram)
    #plt.show()
    
    plt.figure()
    plt.title("Estimated sound source count")
    plt.hist(np.argmax(spectrogram, axis=0)*5)
    plt.xticks(ss_dirs[::10])
    plt.xlabel("azimuth [deg]")
    plt.ylabel("count")
    plt.show()



