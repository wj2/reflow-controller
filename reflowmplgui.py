
import time
import Tkinter as tk
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import matplotlib.animation as mplanim

def _coord_in_rect(xy, rect):
    return (rect.get_x() <= xy[0] < rect.get_x() + rect.get_width() and
            rect.get_y() <= xy[1] < rect.get_y() + rect.get_height())

class ReflowMPLGui(object):

    def __init__(self, reflow):
        self._reflow = reflow
        self._f = plt.figure(figsize=(12, 6))
        spec = gs.GridSpec(6, 12)

        self._profile_ax = self._f.add_subplot(spec[:,2:])
        l = self._reflow.get_profile()
        self._pl = self._profile_ax.plot(l[0], l[1])[0]
        self._rects = self._label_regions(l, self._profile_ax)

        self._start_ax = self._f.add_subplot(spec[0, 0])
        self._startb = plt.Button(self._start_ax, 'start')
        self._startb.on_clicked(self._start_clicked)

        self._abort_ax = self._f.add_subplot(spec[1, 0])
        self._abortb = plt.Button(self._abort_ax, 'abort')
        self._abortb.on_clicked(self._abort_clicked)

        self._active = False
        self._anim = mplanim.FuncAnimation(self._f, self._update_actual_profile,
                                           interval=1000)
        self._f.canvas.mpl_connect('button_release_event', self._on_release)
        plt.show()

    def _update_wanted_profile(self):
        l = self._reflow.get_profile()
        self._pl.set_data(l[0], l[1])
        self._profile_ax.set_xlim(min(l[0]), max(l[0]))
        self._rects = self._label_regions(l, self._profile_ax, self._rects)
        plt.draw()        

    def _get_profile_change(self, label):
        temp, time, pwr = self._reflow.get_properties(label)
        
        m = tk.Tk()
        tk.Label(m, text=label+'time:').grid(row=0)
        tk.Label(m, text=label+'temp:').grid(row=1)
        tk.Label(m, text=label+'pwr:').grid(row=2)
        gtime = tk.Entry(m)
        gtime.grid(row=0, column=1)
        gtime.insert(10, str(time))
        gtemp = tk.Entry(m)
        gtemp.grid(row=1, column=1)
        gtemp.insert(10, str(temp))
        gpwr = tk.Entry(m)
        gpwr.grid(row=2, column=1)
        gpwr.insert(10, str(pwr))
        tk.Button(m, text='Okay', command=m.quit).grid(row=4, column=0, 
                                                       sticky=tk.W, pady=4)
        m.mainloop()
        new_time = gtime.get()
        new_temp = gtemp.get()
        new_pwr = gpwr.get()
        m.destroy()
        self._reflow.set_properties(label, new_temp, new_time, new_pwr)
        self._update_wanted_profile()
        return new_time, new_temp, new_pwr

    def _on_release(self, event):
        if not self._active and event.inaxes is self._profile_ax:
            for r in self._rects:
                if _coord_in_rect((event.xdata, event.ydata), r):
                    self._get_profile_change(r.get_label())
                    
    def _label_regions(self, profile, add_axis, rects=None):
        xs, ys, labels, _ = profile
        bot, top = add_axis.get_ylim()
        if rects is None:
            pht = plt.Rectangle((xs[0], bot), xs[1]-xs[0], top, alpha=.5, color='g', 
                                label=labels[0])
            add_axis.add_artist(pht)
            soak = plt.Rectangle((xs[1], bot), xs[2]-xs[1], top, alpha=.5, color='r', 
                                 label=labels[1])
            add_axis.add_artist(soak)
            dwell = plt.Rectangle((xs[2], bot), xs[3]-xs[2], top, alpha=.5, color='b', 
                                  label=labels[2])
            add_axis.add_artist(dwell)
            reflow = plt.Rectangle((xs[3], bot), xs[4]-xs[3], top, alpha=.5, color='y',
                                   label=labels[3])
            add_axis.add_artist(reflow)
        else:
            pht, soak, dwell, reflow = rects
            for i,r in enumerate(rects):
                r.set_x(xs[i])
                r.set_y(bot)
                r.set_width(xs[i+1]-xs[i])
                r.set_height(top)

        return pht, soak, dwell, reflow

    def _start_clicked(self, event):
        if not self._active:
            self._active = True
            self._reflow.send_profile_to_controller()
            self._reflow.start()
            self._tt = self._reflow.get_total_time()
            self._al = self._profile_ax.plot([], [])[0]
            self._al_nums = ([], [])

    def _update_actual_profile(self, event):
        if self._active:
            s, t = self._reflow.get_temp_and_time()
            if s != -1 and t != -1:
                self._al_nums[0].append(s)
                self._al_nums[1].append(t)
                self._al.set_data(*self._al_nums)
                plt.draw()
                if s > self._tt:
                    self._active = False
                    self._reflow.okay()

    def _abort_clicked(self, event):
        self._active = False
        self._reflow.stop()
        self._al_nums = ([], [])
        self._al.set_data([], [])
        plt.draw()

