import time
import numpy as np
import matplotlib.pyplot as plt

from picoscope import ps5000a
from LabOnChip.HelperFunctions import fit_decay, mono_exp_decay


class Picoscope:
    def __init__(self, *args, **kwargs):
        super(Picoscope, self).__init__()
        self.ps = ps5000a.PS5000a(connect=False)

    def openScope(self):
        self.ps.open()

        bitRes = 16
        self.ps.setResolution(str(bitRes))
        print("Resolution =  %d Bit" % bitRes)

        self.ps.setChannel("A", coupling="DC", VRange=10.0, VOffset=-8.0, enabled=True)
        self.ps.setChannel("B", coupling="DC", VRange=5.0, VOffset=0, enabled=False)
        self.ps.setSimpleTrigger(trigSrc="External", threshold_V=2.0, direction="Falling", timeout_ms=5000)

        # Set capture duration, s
        waveformDuration = 100E-3
        obsDuration = 1*waveformDuration

        # Set sampling rate, Hz
        sampleFreq = 1E4
        sampleInterval = 1.0 / sampleFreq

        res = self.ps.setSamplingInterval(sampleInterval, obsDuration)
        self.res = res

        # Print final capture settings
        print("Sampling frequency = %.3f MHz" % (1E-6/res[0]))
        print("Sampling interval = %.f ns" % (res[0] * 1E9))
        print("Taking  samples = %d" % res[1])
        print("Maximum samples = %d" % res[2])

    def closeScope(self):
        self.ps.close()

    def armMeasure(self):
        self.ps.runBlock()

    def measure(self):
        # print("Waiting for trigger")
        while not self.ps.isReady():
            time.sleep(0.001)
        # print("Sampling Done")
        return self.ps.getDataV("A")

    def show_signal(self):
        """ Measure a single decay and show with the fit in a plot. """

        # Create a time axis for the plots
        x = np.arange(self.res[1]) * self.res[0]
        x *= 1E3  # Convert to milliseconds

        # Collect data
        self.armMeasure()
        data = self.measure()

        # Calculate lifetime
        popt = fit_decay(x, data)
        residuals = data - mono_exp_decay(x, *popt)
        standd = np.std(residuals)

        # Do plots
        fig, (ax1, ax2) = plt.subplots(2,figsize=(15, 15), sharex=False)
        # creating a timer object and setting an interval of 3000 milliseconds
        timer = fig.canvas.new_timer(interval=3000)
        timer.add_callback(plt.close)

        ax1.set_title("Lifetime is {0:.4f} $\pm$ {1:.4f} ms".format(popt[1], standd))

        ax1.plot(x, data, 'k.', label="Original Noised Data")
        ax1.plot(x, mono_exp_decay(x, *popt), 'r-', label="Fitted Curve")
        ax1.axvline(popt[1], color='blue')
        ax1.grid(True, which="major")
        ax1.set_ylabel('Intensity (A.U.)')
        ax1.set_xlim(0, max(x))
        ax1.axhline(y=0, color='k')
        ax1.legend()

        ax2.set_xlabel("Time (ms)")
        ax2.set_ylabel('Residuals')
        ax2.axhline(y=0, color='k')
        ax2.plot(x, residuals)
        ax2.set_xlim(0, max(x))
        ax2.grid(True, which="major")

        # Bring window to the front (above pycharm)
        fig.canvas.manager.window.activateWindow()
        fig.canvas.manager.window.raise_()
        timer.start()
        plt.show()
