
#!/usr/bin/env python

# The version of this script showing up at check-in should run the experiment
# in the version of realtime_receiver.py distributed with AFNI, but using a
# PsychoPy interface, instead of the original wx/Matplotlib GUI.  All of the
# code to run this GUI is still present, but is commented out with the string,
# '# For orig wx demo # '.  To recover the functionality of the original GUI,
# remove all occurences of this string, and comment out the 'if True' statment
# indicated below, below the 'if self.demo_frame' statement .

import sys
import logging
from   optparse import OptionParser

import numpy as np

import afniInterfaceRT as nf

# For orig wx demo # # must use matplotlib with wx, not pylab
# For orig wx demo # try:
   # For orig wx demo # import wx
# For orig wx demo # except ImportError:
    # For orig wx demo # pass

# For orig wx demo # try:
   # For orig wx demo # import matplotlib
   # For orig wx demo # matplotlib.use('WXAgg')

   # For orig wx demo # # set some resource font values
   # For orig wx demo # matplotlib.rc('axes', titlesize=11)
   # For orig wx demo # matplotlib.rc('axes', labelsize=9)
   # For orig wx demo # matplotlib.rc('xtick', labelsize=8)
   # For orig wx demo # matplotlib.rc('ytick', labelsize=7)

   # For orig wx demo # from   matplotlib.backends.backend_wxagg import FigureCanvasWx as FigureCanvas
   # For orig wx demo # from   matplotlib.backends.backend_wxagg import NavigationToolbar2Wx
   # For orig wx demo # from   matplotlib.figure import Figure

   # For orig wx demo # from   matplotlib.ticker import FormatStrFormatter
# For orig wx demo # except ImportError:
    # For orig wx demo # pass
    
from   psychopy import visual, core # , sound



class DemoExperiment(object):

   def __init__(self, options):

      self.TR_data      = []

      # dc_params = [P1, P2]
      # P1 = dr low limit, P2 = scalar -> [0,1]
      # result is (dr-P1)*P2  {applied in [0,1]}
      self.dc_params    = []

      # For orig wx demo # self.demo_frame   = None  # for demo plot
      # For orig wx demo # self.wx_app       = None  # wx App for demo plot
      self.show_data    = options.show_data

      print ("++ Initializing experiment stimuli")
      self.setupExperiment()



   def setupExperiment(self):

      """create the GUI for display of the demo data"""

      # self.exptWindow = visual.Window(fullscr=options.fullscreen, allowGUI=False)
      self.exptWindow = visual.Window([1280, 720], allowGUI=False)

      # For this demonstration experiement, set corners of the "active area" (where
      # we will "draw") to be a square in the middle of a 16:9 screen.
      self.nPlotPoints  = 10
      self.xMax         = 0.50625
      self.xMin         = self.xMax * -1.0
      self.xDelta       = (self.xMax - self.xMin) / (1.0 * self.nPlotPoints)
      self.yMax         = 0.9
      self.yMin         = self.yMax * -1.0
      self.yDelta       = (self.yMax - self.yMin) / (1.0 * self.nPlotPoints)

      # Now cut this area up into a series of vertical rectangles that we will draw
      # to when we have results
      self.stimAreaCorners    = [None] * self.nPlotPoints

      for i in range(self.nPlotPoints):
         self.stimAreaCorners[i] = np.array ([[(self.xMin + (self.xDelta*(i+0))), self.yMin], [(self.xMin + (self.xDelta*(i+0))), self.yMax],
                                              [(self.xMin + (self.xDelta*(i+1))), self.yMax], [(self.xMin + (self.xDelta*(i+1))), self.yMin]])

         displayArea = visual.ShapeStim (self.exptWindow, vertices = self.stimAreaCorners[i],
                                         autoLog = False, fillColor = [1, 1, 1])

      self.exptWindow.flip()

      # For orig wx demo # self.wx_app = wx.App()
      # For orig wx demo # self.demo_frame = CanvasFrame(title='receiver demo wx')
      # For orig wx demo # self.demo_frame.EnableCloseButton(True)
      # For orig wx demo # self.demo_frame.Show(True)
      # For orig wx demo # self.demo_frame.style = 'bar'
      # For orig wx demo # self.demo_frame.xlabel = 'most recent 10 TRs'
      # For orig wx demo # self.demo_frame.ylabel = 'scaled diff_ratio'

      # For orig wx demo # # for the current demo, set an ranges for 10 numbers in [0,10]
      # For orig wx demo # if self.demo_frame.style == 'graph':
         # For orig wx demo # self.demo_frame.set_limits(0, 9.1, -0.1, 10.1)
      # For orig wx demo # elif self.demo_frame.style == 'bar':
         # For orig wx demo # self.demo_frame.set_limits(0, 10.1, -0.1, 10.1)



   def runExperiment (self, data):

      for i in range(self.nPlotPoints):
         if (len(data) - 1 - i) > 0:
            plotIndex = self.nPlotPoints - 1 - i
            self.stimAreaCorners[plotIndex] = np.array ([
                  [(self.xMin + (self.xDelta*(plotIndex+0))), self.yMin],
                  [(self.xMin + (self.xDelta*(plotIndex+0))), self.yMin + self.yDelta * data[len(data) - 1 - i][0]],
                  [(self.xMin + (self.xDelta*(plotIndex+1))), self.yMin + self.yDelta * data[len(data) - 1 - i][0]],
                  [(self.xMin + (self.xDelta*(plotIndex+1))), self.yMin]
                                                                      ])

            displayArea = visual.ShapeStim (self.exptWindow, vertices = self.stimAreaCorners[i],
                                            autoLog = False, fillColor = [-1, -1, 1])
            displayArea.draw()

      self.exptWindow.flip()




   def process_demo_data(self):

      length = len(self.TR_data)
      if length == 0:
         return

      if self.show_data:
         print('-- TR %d, demo value: %s' % (length, self.TR_data[length - 1][0]))
      # For orig wx demo # if self.demo_frame:
      if True: # Comment out this line if using wx/Matplotlib GUI toolkit
         if length > 10:
            bot = length - 10
         else:
            bot = 0
         pdata = [self.TR_data[ind][0] for ind in range(bot, length)]

         # For orig wx demo # self.demo_frame.plot_data(pdata)

         self.runExperiment(self.TR_data)




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

         return extra[0:npairs]    # return the partial list

      # # failure!
      # else:
      #     print("** invalid data_choice '%s', shutting down ..." % rec.data_choice)
      #     return -1, []



# ======================================================================
# general plotting routine:
#

# For orig wx demo # def plot(data, title=''):

   # For orig wx demo # """plot data"""

   # For orig wx demo # frame = CanvasFrame(title=title)

   # For orig wx demo # if title == '':
      # For orig wx demo # title = 'basic plot'
   # For orig wx demo # frame.SetTitle(title)

   # For orig wx demo # frame.Show(True)
   # For orig wx demo # frame.plot_data(data)

   # For orig wx demo # return 0, frame



# For orig wx demo # # ======================================================================
# For orig wx demo # # main plotting canvas class

# For orig wx demo # class CanvasFrame(wx.Frame):

   # For orig wx demo # """create a main plotting canvas
        # For orig wx demo # title   : optional window title
   # For orig wx demo # """

   # For orig wx demo # counter = 0

   # For orig wx demo # def __init__(self, title=''):

      # For orig wx demo # wx.Frame.__init__(self, None, -1, title, size=(400, 300))
      # For orig wx demo # self.figure = Figure()
      # For orig wx demo # self.canvas = FigureCanvas(self, -1, self.figure)
      # For orig wx demo # self.sizer = wx.BoxSizer(wx.VERTICAL)
      # For orig wx demo # self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
      # For orig wx demo # self.SetSizer(self.sizer)
      # For orig wx demo # self.Fit()

      # For orig wx demo # # axis plotting info
      # For orig wx demo # self.ax = None
      # For orig wx demo # self.xmin = 1.0
      # For orig wx demo # self.xmax = 0.0
      # For orig wx demo # self.ymin = 1.0
      # For orig wx demo # self.ymax = 0.0
      # For orig wx demo # self.xlabel = ''
      # For orig wx demo # self.ylabel = ''
      # For orig wx demo # self.style = 'graph'

      # For orig wx demo # self.images = []

      # For orig wx demo # self.toolbar = NavigationToolbar2Wx(self.canvas)
      # For orig wx demo # self.toolbar.Realize()
      # For orig wx demo # self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
      # For orig wx demo # self.toolbar.update()



   # For orig wx demo # def cb_keypress(self, event):

      # For orig wx demo # if event.key == 'q':
         # For orig wx demo # self.Close()



   # For orig wx demo # def set_limits(self, xmin=1.0, xmax=0.0, ymin=1.0, ymax=0.0):

      # For orig wx demo # """if xmin < xmax: apply, and similarly for y"""

      # For orig wx demo # if xmin < xmax:
         # For orig wx demo # self.xmin = xmin
         # For orig wx demo # self.xmax = xmax
         # For orig wx demo # print('-- resetting xlimits to:', xmin, xmax)

      # For orig wx demo # if ymin < ymax:
         # For orig wx demo # self.ymin = ymin
         # For orig wx demo # self.ymax = ymax
         # For orig wx demo # print('-- resetting ylimits to:', ymin, ymax)



   # For orig wx demo # def plot_data(self, data, title=''):

      # For orig wx demo # """plot data
         # For orig wx demo # style can be 'graph' or 'bar'"""

      # For orig wx demo # if self.ax is None:
         # For orig wx demo # self.ax = self.figure.add_subplot(1, 1, 1, title=title)

      # For orig wx demo # self.ax.clear()

      # For orig wx demo # if self.style == 'graph':
         # For orig wx demo # self.ax.plot(data)
         # For orig wx demo # self.ax.grid(True)
      # For orig wx demo # else:     # bars of width 1
         # For orig wx demo # offsets = np.arange(len(data))
         # For orig wx demo # bars = self.ax.bar(offsets, data, 1)

      # For orig wx demo # self.ax.set_xlabel(self.xlabel)
      # For orig wx demo # self.ax.set_ylabel(self.ylabel)

      # For orig wx demo # # after data is plotted, set limits
      # For orig wx demo # if self.xmin < self.xmax:
         # For orig wx demo # self.ax.set_xlim((self.xmin, self.xmax))
      # For orig wx demo # if self.ymin < self.ymax:
         # For orig wx demo # self.ax.set_ylim((self.ymin, self.ymax))

      # For orig wx demo # self.Fit()        # maybe not applied without a running app loop
      # For orig wx demo # self.canvas.draw()



   # For orig wx demo # def exit(self):

      # For orig wx demo # self.Destroy()



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

