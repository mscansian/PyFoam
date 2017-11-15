"""
Application-class that implements pyFoamClearCase.py
"""
import sys

from optparse import OptionGroup

from .PyFoamApplication import PyFoamApplication

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from PyFoam.ThirdParty.six import print_

class ClearCase(PyFoamApplication):
    def __init__(self,
                 args=None,
                 **kwargs):
        description="""\
Removes all timesteps but the first from a case-directory.  Also
removes other data that is generated by sovers/utilities/PyFoam
"""
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog <caseDirectory>",
                                   interspersed=True,
                                   changeVersion=False,
                                   nr=1,
                                   exactNr=False,
                                   **kwargs)

    def addOptions(self):
        what=OptionGroup(self.parser,
                         "What",
                         "Define what should be cleared")
        self.parser.add_option_group(what)

        what.add_option("--after",
                        type="float",
                        dest="after",
                        default=None,
                        help="Only remove timesteps after this time")
        what.add_option("--processors-remove",
                        action="store_true",
                        dest="processor",
                        default=False,
                        help="Remove the processor directories")
        what.add_option("--vtk-keep",
                        action="store_false",
                        dest="vtk",
                        default=True,
                        help="Keep the VTK directory")
        what.add_option("--no-pyfoam",
                        action="store_false",
                        dest="pyfoam",
                        default=True,
                        help="Keep the PyFoam-specific directories and logfiles")
        what.add_option("--remove-analyzed",
                        action="store_true",
                        dest="removeAnalyzed",
                        default=False,
                        help="Also remove the directories thatend with 'analyzed' (usually created by PyFoam)")
        what.add_option("--keep-last",
                        action="store_true",
                        dest="latest",
                        default=False,
                        help="Keep the data from the last time-step")
        what.add_option("--keep-regular",
                        action="store_true",
                        dest="keepRegular",
                        default=False,
                        help="Keep all the 'regular' timesteps")
        what.add_option("--keep-parallel",
                        action="store_true",
                        dest="keepParallel",
                        default=False,
                        help="Keep all the timesteps in the processor-directories")
        what.add_option("--keep-interval",
                        action="store",
                        type=float,
                        dest="keepInterval",
                        default=None,
                        help="Keep timesteps that are this far apart")
        what.add_option("--keep-postprocessing",
                        action="store_true",
                        dest="keepPostprocessing",
                        default=False,
                        help="Keep the directory 'postProcessing' where functionObjects write their stuff")
        what.add_option("--additional",
                        action="append",
                        dest="additional",
                        default=[],
                        help="Glob-pattern with additional files to be removes. Can be used more than once")
        what.add_option("--clear-history",
                        action="store_true",
                        dest="clearHistory",
                        default=False,
                        help="Clear the PyFoamHistory-file")
        what.add_option("--no-clear-parameters",
                        action="store_false",
                        dest="clearParameters",
                        default=True,
                        help="Don't clear the PyFoamPrepareCaseParameters-file")
        what.add_option("--function-object-data",
                        action="store_true",
                        dest="functionObjectData",
                        default=False,
                        help="Clear data written by functionObjects. Only works if the data directory has the same name as the functionObject")

        output=OptionGroup(self.parser,
                         "Output",
                         "What information should be given")
        self.parser.add_option_group(output)
        output.add_option("--fatal",
                          action="store_true",
                          dest="fatal",
                        default=False,
                        help="If non-cases are specified the program should abort")
        output.add_option("--silent",
                          action="store_true",
                          dest="silent",
                          default=False,
                          help="Don't complain about non-case-files")
        output.add_option("--verbose-cases",
                          action="store_true",
                          dest="verbose",
                          default=False,
                          help="Print what cases are cleared")
        output.add_option("--verbose-clear",
                          action="store_true",
                          dest="verboseClear",
                          default=False,
                          help="Print what is being cleared during clearing")

    def run(self):
        if not self.opts.keepPostprocessing:
            self.opts.additional.append("postProcessing")

        notCleared=[]

        for cName in self.parser.getArgs():
            if self.checkCase(cName,fatal=self.opts.fatal,verbose=not self.opts.silent):
                try:
                    self.addLocalConfig(cName)

                    if self.opts.verbose:
                        print_("Clearing",cName)

                    sol=SolutionDirectory(cName,
                                          archive=None,
                                          parallel=True,
                                          paraviewLink=False)
                    sol.clear(after=self.parser.getOptions().after,
                              processor=self.parser.getOptions().processor,
                              pyfoam=self.parser.getOptions().pyfoam,
                              vtk=self.parser.getOptions().vtk,
                              verbose=self.parser.getOptions().verboseClear,
                              removeAnalyzed=self.parser.getOptions().removeAnalyzed,
                              keepRegular=self.parser.getOptions().keepRegular,
                              keepParallel=self.parser.getOptions().keepParallel,
                              keepLast=self.parser.getOptions().latest,
                              keepInterval=self.parser.getOptions().keepInterval,
                              clearHistory=self.parser.getOptions().clearHistory,
                              clearParameters=self.parser.getOptions().clearParameters,
                              additional=self.parser.getOptions().additional,
                              functionObjectData=self.parser.getOptions().functionObjectData)

                    self.addToCaseLog(cName)
                except OSError:
                    e = sys.exc_info()[1] # compatible with 2.x and 3.x
                    self.warning("Can not clear",cName,"because of OSError",e)
                    notCleared.append(cName)

        if len(notCleared)>0:
            self.warning("These case not cleared because of OS-problems:",
                         ", ".join(notCleared))
