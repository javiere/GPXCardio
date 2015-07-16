"""
Reads the cardio data from GPX files and generates plots with it

Author: Javier Espigares Martin
Email: javierespigares@gmail.com
"""
from datetime import datetime, date, time


class GPXCardio():

  """
  GPX Cardio class. Opens the filename given by parameters. Obtains the
  relevant data and returns it in a python friendly manner. It can also produce a
  plot with the heart rate information from the fetched data
  """

  def __init__(self, filename, verbose=False):
    """
    Initializes the object:

    parameters:
     - filename: Filename to open
     - verbose: Prints out information of the opened file as it is
                encountered
    """
    import xml.etree.ElementTree as ET

    self.__filename__ = filename
    self.__verbose__ = verbose
    if verbose:
      print "Parsing", filename
    tree = ET.parse(filename)
    self.__root__ = tree.getroot()
    self.__nsdic__ = {"default": "http://www.topografix.com/GPX/1/1",
                      "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                      "schemaLocation": "",
                      "gpxtpx": "http://www.garmin.com/xmlschemas/TrackPointExtension/v1",
                      "gpxx": "http://www.garmin.com/xmlschemas/GpxExtensions/v3"}

  def getCardio(self):
    """
    Returns the cardio data from the GPX file as a list with the format:
    (datetime,heart rate [bpm])  Where datetime is an object datetime.datetime
    and heart rate is a float. The list is also stored in the class. If the
    method is called a second time it will return the existing list rather
    than reading it onece again

    If the file does not contain hear rate information, the it returns an
    empty list.
    """
    if hasattr(self, '__heart_rate__'):
      return self.__heart_rate__
    self.__heart_rate__ = []
    for pt in self.__root__[1][1].findall('.//default:trkpt', self.__nsdic__):
      hr = pt.find('.//gpxtpx:hr', self.__nsdic__).text
      tm = pt.find('.//default:time', self.__nsdic__).text
      # Divides the data/time string into the different parts using
      # the standard format found in files.
      #  YYYY-MM-DDTHH:MM:SSZ
      tm = tm.split('T')
      dt = tm[0].split('-')
      d = date(int(dt[0]), int(dt[1]), int(dt[2]))
      dt = tm[1][0:len(tm[1]) - 1]
      dt = dt.split(':')
      t = time(int(dt[0]), int(dt[1]), int(dt[2]))
      del(tm)
      tm = datetime.combine(d, t)
      self.__heart_rate__.append((tm, float(hr)))
    if self.__verbose__:
      print "Heart Rate record for ", self.__filename__
      for i in self.__heart_rate__:
        print "Time :", i[0], " HR: ", i[1]
    return self.__heart_rate__

  def plotCardio(self):
    """
    Produces a plot of the heart rate information found in the opened file.

    Returns a matplotlib.pyplot object with the plot description
    """
    import matplotlib.pyplot as plt

    self.getCardio()
    initial_datetime = self.__heart_rate__[0][0]
    hrpts = map(lambda x: x[1], self.__heart_rate__)
    timepts = map(lambda x: (x[0] - initial_datetime).seconds,
                  self.__heart_rate__)

    plt.plot(timepts, hrpts, 'ro')
    plt.ylabel("Heart Rate [bpm]")
    plt.xlabel("Seconds from begining")

    return plt, hrpts, timepts


def compare_hr_run(filename1, filename2, descriptor1='1st HR',
                   descriptor2='2nd HR', verbose=False):
  """
  Method to generate a plot comparison between two gpx runs
  """
  import matplotlib.pyplot as plt
  run1 = GPXCardio(filename1, verbose)
  run2 = GPXCardio(filename2, verbose)
  cardio1 = run1.getCardio()
  cardio2 = run2.getCardio()

  # Assume 1st file goes first in time
  def pts_fun(it, hr):
    t = map(lambda x: (x[0] - it).seconds, hr)
    hr = map(lambda x: x[1], hr)
    return t, hr

  initial_time = cardio1[0][0]
  f1_time, f1_hr = pts_fun(initial_time, cardio1)
  f2_time, f2_hr = pts_fun(initial_time, cardio2)
  lines = plt.plot(f1_time, f1_hr, 'r', f2_time, f2_hr, 'b')
  plt.ylabel("Heart Rate [bpm]")
  plt.xlabel("Seconds from begining")
  plt.title("Heart Rate Monitor Comparison")
  plt.grid(True)
  plt.figlegend((lines), (descriptor1, descriptor2), 'lower right')

  plt.show()

if __name__ == "__main__":
  compare_hr_run('data/Garmin.gpx', 'data/Microsoft.gpx', 'Garmin', 'MS Band')
