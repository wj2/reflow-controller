
import time
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import matplotlib.animation as mplanim

class ReflowMPLGui(object):

    def __init__(self, reflow):
        self._reflow = reflow
        self._f = plt.figure(figsize=(10, 6))
        spec = gs.GridSpec(6, 10)

        self._profile_ax = self._f.add_subplot(spec[:,1:])
        l = self._reflow.get_profile()
        self._pl = self._profile_ax.plot(l[0], l[1])[0]

        self._start_ax = self._f.add_subplot(spec[0, 0])
        self._startb = plt.Button(self._start_ax, 'start')
        self._startb.on_clicked(self._start_clicked)

        self._abort_ax = self._f.add_subplot(spec[1, 0])
        self._abortb = plt.Button(self._abort_ax, 'abort')
        self._abortb.on_clicked(self._abort_clicked)

        self._active = False
        self._anim = mplanim.FuncAnimation(self._f, self._update_actual_profile,
                                           interval=1000)
        plt.show()

    def _start_clicked(self, event):
        if not self._active:
            self._active = True
            self._reflow.send_profile_to_controller()
            self._reflow.start()
            self._al = self._profile_ax.plot([], [])[0]
            self._al_nums = ([], [])

    def _update_actual_profile(self, event):
        if self._active:
            s, t = self._reflow.get_temp_and_time()
            self._al_nums[0].append(s)
            self._al_nums[1].append(t)
            self._al.set_data(*self._al_nums)
            plt.draw()

    def _abort_clicked(self, event):
        self._active = False
        self._reflow.stop()
        self._al.nums = ([], [])
        self._al.set_data([], [])
        plt.draw()

