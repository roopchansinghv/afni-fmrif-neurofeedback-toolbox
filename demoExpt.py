
#!/usr/bin/env python

import sys
import logging
from   optparse import OptionParser

import numpy as np

import afniInterfaceRT as nf

# must use matplotlib with wx, not pylab
try:
   import wx
except ImportError:
    pass

try:
   import matplotlib
   matplotlib.use('WXAgg')

   # set some resource font values
   matplotlib.rc('axes', titlesize=11)
   matplotlib.rc('axes', labelsize=9)
   matplotlib.rc('xtick', labelsize=8)
   matplotlib.rc('ytick', labelsize=7)

   from   matplotlib.backends.backend_wxagg import FigureCanvasWx as FigureCanvas
   from   matplotlib.backends.backend_wxagg import NavigationToolbar2Wx
   from   matplotlib.figure import Figure

   from   matplotlib.ticker import FormatStrFormatter
except ImportError:
    pass
    
from   psychopy import visual, core # , sound



class DemoExperiment(object):

   def __init__(self, options):

      self.TR_data      = []

      # dc_params = [P1, P2]
      # P1 = dr low limit, P2 = scalar -> [0,1]
      # result is (dr-P1)*P2  {applied in [0,1]}
      self.dc_params    = []

      self.demo_frame   = None  # for demo plot
      self.wx_app       = None  # wx App for demo plot
      self.show_data    = options.show_data

      print ("++ Initializing experiment stimuli")
      self.setupExperiment()



   def setupExperiment(self):

      """create the GUI for display of the demo data"""

      # self.exptWindow = visual.Window(fullscr=options.fullscreen, allowGUI=False)
      self.exptWindow = visual.Window([1280, 720], allowGUI=False)

      # For this demonstration experiement, set corners of the "active area" (where
      # we will "draw") to be a square in the middle of a 16:9 screen.
      self.stimAreaCorners = np.array ([[-0.50625, -0.9], [-0.50625, 0.9],
                                        [0.50625, 0.9], [0.50625, -0.9]])

      displayArea = visual.ShapeStim (self.exptWindow, vertices = self.stimAreaCorners,
                                      autoLog = False, fillColor = [1, -1, -1])
      displayArea.draw()
      self.exptWindow.flip()

      self.mask = np.tile("Receiver Demo Using PsychoPy", (16, 9))
      self.boxList = list(range(0, 144))

      self.wx_app = wx.App()
      self.demo_frame = CanvasFrame(title='receiver demo wx')
      self.demo_frame.EnableCloseButton(True)
      self.demo_frame.Show(True)
      self.demo_frame.style = 'bar'
      self.demo_frame.xlabel = 'most recent 10 TRs'
      self.demo_frame.ylabel = 'scaled diff_ratio'

      # for the current demo, set an ranges for 10 numbers in [0,10]
      if self.demo_frame.style == 'graph':
         self.demo_frame.set_limits(0, 9.1, -0.1, 10.1)
      elif self.demo_frame.style == 'bar':
         self.demo_frame.set_limits(0, 10.1, -0.1, 10.1)



   def runExperiment (self):

      # As the original demostration runs, in parallel, we will swap colors between
      # red and blue for every volume receive.  This is just to verify initially we
      # can draw and update "exptWindow" for every volume of data received.
      if (len(self.TR_data) % 2):
         displayArea = visual.ShapeStim (self.exptWindow, vertices = self.stimAreaCorners,
                                         autoLog = False, fillColor = [-1, -1, 1])
      else:
         displayArea = visual.ShapeStim (self.exptWindow, vertices = self.stimAreaCorners,
                                         autoLog = False, fillColor = [1, -1, -1])
      displayArea.draw()
      self.exptWindow.flip()




   def process_demo_data(self):

      length = len(self.TR_data)
      if length == 0:
         return

      if self.show_data:
         print('-- TR %d, demo value: %s' % (length, self.TR_data[length - 1][0]))
      if self.demo_frame:
         if length > 10:
            bot = length - 10
         else:
            bot = 0
         pdata = [self.TR_data[ind][0] for ind in range(bot, length)]
         self.demo_frame.plot_data(pdata)



   def compute_TR_data(self, motion, extra):

      """If writing to the serial port, this is the main function to compute
      results from motion and/or extras for the current TR and
      return it as an array of floats.

      Note that motion and extras are lists of time series of length nread,
      so processing a time series is easy, but a single TR requires extracting
      the data from the end of each list.

      The possible computations is based on data_choice, specified by the user
      option -data_choice.  If you want to send data that is not listed, just
      add a condition.

      ** Please add each data_choice to the -help.  Search for motion_norm to
      find all places to edit.

      return 2 items:
          error code:     0 on success, -1 on error
          data array:     (possibly empty) array of data to send
      """

      print("++ Entering compute TR data")

      # # case 'motion': send all motion
      # if rec.data_choice == 'motion':
      #     if rti.nread > 0:
      #         return 0, [rti.motion[ind][rti.nread - 1] for ind in range(6)]
      #     else:
      #         return -1, []

      # # case 'motion_norm': send Euclidean norm of motion params
      # #                     --> sqrt(sum of squared motion params)
      # elif rec.data_choice == 'motion_norm':
      #     if rti.nread > 0:
      #         motion = [rti.motion[ind][rti.nread - 1] for ind in range(6)]
      #         return 0  # , [UTIL.euclidean_norm(motion)]
      #     else:
      #         return -1, []

      # # case 'all_extras': send all extra data
      # elif rec.data_choice == 'all_extras':
      #     if rti.nextra > 0:
      #         return 0, [rti.extras[i][rti.nread - 1] for i in range(rti.nextra)]
      #     else:
      #         return -1, []

      # # case 'diff_ratio': (a-b)/(abs(a)+abs(b))
      # elif rec.data_choice == 'diff_ratio':

      npairs = len(extra) // 2
      print(npairs)
      if npairs <= 0:
          print('** no pairs to compute diff_ratio from...')
          return None

      # modify extra array, setting the first half to diff_ratio
      for ind in range(npairs):
         a = extra[2 * ind]
         b = extra[2 * ind + 1]
         if a == 0 and b == 0:
            newval = 0.0
         else:
            newval = (a - b) / float(abs(a) + abs(b))

         # --------------------------------------------------------------
         # VERY data dependent: convert from diff_ratio to int in {0..10}
         # assume AFNI_data6 demo                             15 Jan
         # 2013

         # now scale [bot,inf) to {0..10}, where val>=top -> 10
         # AD6: min = -0.1717, mean = -0.1605, max = -0.1490

         bot = -0.17         # s620: bot = 0.008, scale = 43.5
         scale = 55.0        # =~ 1.0/(0.1717-0.149), rounded up
         if len(self.dc_params) == 2:
            bot = self.dc_params[0]
            scale = self.dc_params[1]

         val = newval - bot
         if val < 0.0:
            val = 0.0
         ival = int(10 * val * scale)
         if ival > 10:
            ival = 10

         extra[ind] = ival

         print('++ diff_ratio: ival = %d (from %s), (params = %s)' %
               (ival, newval, self.dc_params))

         # save data and process
         self.TR_data.append(extra[0:npairs])
         self.process_demo_data()

         self.runExperiment()

         return extra[0:npairs]    # return the partial list

      # # failure!
      # else:
      #     print("** invalid data_choice '%s', shutting down ..." % rec.data_choice)
      #     return -1, []



# ======================================================================
# general plotting routine:
#

def plot(data, title=''):

   """plot data"""

   frame = CanvasFrame(title=title)

   if title == '':
      title = 'basic plot'
   frame.SetTitle(title)

   frame.Show(True)
   frame.plot_data(data)

   return 0, frame



# ======================================================================
# main plotting canvas class

class CanvasFrame(wx.Frame):

   """create a main plotting canvas
        title   : optional window title
   """

   counter = 0

   def __init__(self, title=''):

      wx.Frame.__init__(self, None, -1, title, size=(400, 300))
      self.figure = Figure()
      self.canvas = FigureCanvas(self, -1, self.figure)
      self.sizer = wx.BoxSizer(wx.VERTICAL)
      self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
      self.SetSizer(self.sizer)
      self.Fit()

      # axis plotting info
      self.ax = None
      self.xmin = 1.0
      self.xmax = 0.0
      self.ymin = 1.0
      self.ymax = 0.0
      self.xlabel = ''
      self.ylabel = ''
      self.style = 'graph'

      self.images = []

      self.toolbar = NavigationToolbar2Wx(self.canvas)
      self.toolbar.Realize()
      self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
      self.toolbar.update()



   def cb_keypress(self, event):

      if event.key == 'q':
         self.Close()



   def set_limits(self, xmin=1.0, xmax=0.0, ymin=1.0, ymax=0.0):

      """if xmin < xmax: apply, and similarly for y"""

      if xmin < xmax:
         self.xmin = xmin
         self.xmax = xmax
         print('-- resetting xlimits to:', xmin, xmax)

      if ymin < ymax:
         self.ymin = ymin
         self.ymax = ymax
         print('-- resetting ylimits to:', ymin, ymax)



   def plot_data(self, data, title=''):

      """plot data
         style can be 'graph' or 'bar'"""

      if self.ax is None:
         self.ax = self.figure.add_subplot(1, 1, 1, title=title)

      self.ax.clear()

      if self.style == 'graph':
         self.ax.plot(data)
         self.ax.grid(True)
      else:     # bars of width 1
         offsets = np.arange(len(data))
         bars = self.ax.bar(offsets, data, 1)

      self.ax.set_xlabel(self.xlabel)
      self.ax.set_ylabel(self.ylabel)

      # after data is plotted, set limits
      if self.xmin < self.xmax:
         self.ax.set_xlim((self.xmin, self.xmax))
      if self.ymin < self.ymax:
         self.ax.set_ylim((self.ymin, self.ymax))

      self.Fit()        # maybe not applied without a running app loop
      self.canvas.draw()

      # import matplotlib.mlab as mlab
      from matplotlib.pyplot import axis, title, xlabel, hist, grid, show, ylabel, plot
      import pylab

      results = data 

      durations=results

      pylab.figure(figsize=[30,10])
      pylab.subplot(1,3,1)

      n, bins, patches = hist(durations, 50, normed=True, facecolor='blue', alpha=0.75)
      # add a 'best fit' line
      # y = mlab.normpdf( bins, dmean, dstd)
      # plot(bins, durations, 'r--', linewidth=1)
      xlabel('ioHub getEvents Delay')
      ylabel('Percentage')
      title('ioHub Event Delay Histogram)') # (msec.usec):\n'+r'$\ \min={0:.3f},\ \max={1:.3f},\ \mu={2:.3f},\ \sigma={3:.3f}$'.format(
              # dmin, dmax, dmean, dstd))
      # axis([0, dmax+1.0, 0, 25.0])
      grid(True)
      pylab.subplot(1,3,2)
      grid(True)
      pylab.subplot(1,3,3)
      grid(True)
      # show()



   def exit(self):

      self.Destroy()



def processExperimentOptions (self, options=None):

   """
       Process command line options for on-going experiment.
       Customize as needed for your own experiments.
   """

   usage = "%prog [options]"
   description = "AFNI real-time demo receiver with demo visualization."
   parser = OptionParser(usage=usage, description=description)

   parser.add_option("-d", "--debug", action="store_true",
            help="enable debugging output")
   parser.add_option("-v", "--verbose", action="store_true",
            help="enable verbose output")
   parser.add_option("-p", "--tcp_port", help="TCP port for incoming connections")
   parser.add_option("-S", "--show_data", action="store_true",
            help="display received data in terminal if this option is specified")
   parser.add_option("-w", "--swap", action="store_true",
            help="byte-swap numberical reads if set")
   parser.add_option("-f", "--fullscreen", action="store_true",
            help="run in fullscreen mode")

   return parser.parse_args(options)



def main():

   opts, args = processExperimentOptions(sys.argv)

   # print ("Options are " + str(opts))

   if opts.verbose and not opts.debug:
      nf.add_stderr_logger(level=logging.INFO)
   elif opts.debug:
      nf.add_stderr_logger(level=logging.DEBUG)

   print("++ Starting Demo...")
   demo = DemoExperiment(opts)

   # create main interface
   receiver = nf.ReceiverInterface(port=opts.tcp_port, swap=opts.swap,
                                   show_data=opts.show_data)
   if not receiver:
      return 1

   # set signal handlers and look for data
   receiver.set_signal_handlers()  # require signal to exit

   # set receiver callback
   receiver.compute_TR_data = demo.compute_TR_data

   # prepare for incoming connections
   if receiver.RTI.open_incoming_socket():
      return 1

   rv = receiver.process_one_run()
   return rv



if __name__ == '__main__':
   sys.exit(main())

