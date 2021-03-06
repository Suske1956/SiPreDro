import sys
import math
from PyQt5 import QtWidgets
from scipy.optimize import brentq
from PresDr import Ui_MainWindow


class Calculate:
    # class variables
    def __init__(self):
        self.length = 0
        self.length_ok = False
        self.diameter = 0
        self.diameter_ok = False
        self.roughness = 0
        self.roughness_ok = False
        self.density = 0
        self.density_ok = False
        self.dynamic_viscosity = 0
        self.dynamic_viscosity_ok = False
        self.kinematic_viscosity = 0
        self.kinematic_viscosity_ok = False
        self.velocity = 0
        self.velocity_ok = False
        self.flow_rate = 0
        self.flow_rate_ok = False
        self.volume = 0
        self.volume_ok = False
        self.reynolds_number = 0
        self.reynolds_number_ok = False
        self.flow_regime = 'Unknown'
        self.velocity_active = True
        self.dynamic_viscosity_active = True
        self.type_of_conduit = 'Unknown'
        self.line_smooth = False
        self.friction_factor = 0
        self.friction_factor_ok = False
        self.pressure_drop = 0
        self.pressure_drop_ok = False
        self.method = 'Unknown'

    def calculate_start(self):
        self.prerequisites()
        self.determine_relative_roughness()
        self.calculate_friction_factor()
        self.calculate_pressure_drop()

    @staticmethod
    def colebrook_white(x, diameter, roughness, reynolds):
        return (1 / math.sqrt(x)) + 2 * math.log10((roughness / (3.7 * diameter)) + 2.51 / (reynolds * math.sqrt(x)))

    def prerequisites(self):
        # convert velocity into flow rate vice versa triggered by the radio buttons
        if self.velocity_active:
            if self.diameter_ok and self.velocity_ok:
                self.flow_rate = math.pow(self.diameter / 2, 2) * math.pi * self.velocity
                self.flow_rate_ok = True
            else:
                self.flow_rate_ok = False
        else:
            if self.diameter_ok and self.flow_rate_ok and self.diameter > 0:
                self.velocity = self.flow_rate / (math.pow(self.diameter / 2, 2) * math.pi)
                self.velocity_ok = True
            else:
                self.velocity_ok = False

        # convert kinematic into dynamic viscosity vice versa triggered by the radio buttons.
        if self.dynamic_viscosity_active:
            if self.density_ok and self.dynamic_viscosity_ok and self.density > 0:
                self.kinematic_viscosity = self.dynamic_viscosity / self.density
                self.kinematic_viscosity_ok = True
            else:
                self.kinematic_viscosity_ok = False
        else:
            if self.density_ok and self.kinematic_viscosity_ok:
                self.dynamic_viscosity = self.kinematic_viscosity * self.density
                self.dynamic_viscosity_ok = True
            else:
                self.dynamic_viscosity_ok = False

        # Calculate line volume
        if self.length_ok and self.diameter_ok:
            self.volume = self.length * (self.diameter/2)**2*math.pi
            self.volume_ok = True
        else:
            self.volume_ok = False

        # Calculate Reynolds number
        if self.diameter_ok and self.kinematic_viscosity_ok and self.velocity_ok and self.kinematic_viscosity > 0:
            self.reynolds_number = (self.velocity * self.diameter) / self.kinematic_viscosity
            self.reynolds_number_ok = True
            if self.reynolds_number < 2320:
                self.flow_regime = 'Laminar'
            else:
                self.flow_regime = 'Turbulent'
        else:
            self.reynolds_number_ok = False
            self.flow_regime = 'Unknown'

    def determine_relative_roughness(self):
        if self.reynolds_number_ok and self.diameter_ok and self.roughness_ok and self.diameter > 0:
            if self.reynolds_number * self.roughness / self.diameter < 65:
                self.type_of_conduit = 'Smooth conduit'
                self.line_smooth = True
            elif 65 <= self.reynolds_number * self.roughness / self.diameter < 1300:
                self.type_of_conduit = 'Intermediate conduit'
                self.line_smooth = False
            else:
                self.type_of_conduit = 'Rough conduit'
                self.line_smooth = False
        else:
            self.type_of_conduit = 'Unknown'

    def calculate_friction_factor(self):
        if self.reynolds_number_ok and self.diameter_ok and self.roughness_ok and 0 < self.roughness < self.diameter \
                and self.reynolds_number > 0:
            if self.reynolds_number < 2320 and self.line_smooth:
                self.friction_factor = 64/self.reynolds_number
                self.friction_factor_ok = True
                self.method = 'Laminar, Smooth'
            elif 2320 <= self.reynolds_number < 4000 and self.line_smooth:
                self.friction_factor = 0.3164 * math.pow(self.reynolds_number, -0.25)
                self.friction_factor_ok = True
                self.method = 'Blasius'
            else:
                self.friction_factor = brentq(self.colebrook_white, 1e-10, 1e10, args=(
                    self.diameter, self.roughness, self.reynolds_number))
                self.friction_factor_ok = True
                self.method = 'Colebrook White'
        else:
            self.friction_factor_ok = False
            self.method = 'Unknown'

    def calculate_pressure_drop(self):
        if self.friction_factor_ok and self.length_ok and self.diameter_ok and self.velocity_ok and self.density_ok \
                and self. diameter > 0 and self.density > 0 and self.velocity > 0:
            self.pressure_drop = self.friction_factor * self.length /\
                                self.diameter * self.density / 2 * self.velocity ** 2
            self.pressure_drop_ok = True
        else:
            self.pressure_drop_ok = False


class CheckInput:
    def __init__(self):
        self.value_str = None
        self.value_float = 0
        self.input_ok = False
        self.style_string = 'background-color: white;'
        self.popup = QtWidgets.QMessageBox()

    def errormessage(self, text):
        self.popup.setText(text)
        self.popup.setWindowTitle('Input Error')
        self.popup.show()

    def test_input(self):
        if self.value_str != '':
            try:
                self.value_float = float(self.value_str)
            except ValueError:
                self.input_ok = False
                self.style_string = 'background-color: red;'
                self.errormessage('The input cannot be converted to a number')
                return 0
            else:
                self.style_string = 'background-color: white;'
                if self.value_float > 0:
                    self.input_ok = True
                    return self.value_float
                else:
                    self.input_ok = False
                    self.errormessage('The input must be larger than 0')
                    return 0
        else:
            return 0


class Messages:
    def __init__(self):
        self.popup = QtWidgets.QMessageBox()

    def message(self, title, text):
        self.popup.setText(text)
        self.popup.setWindowTitle(title)
        self.popup.show()

    def warning(self, title, text):
        self.popup.setIcon(QtWidgets.QMessageBox.Warning)
        self.popup.setText(text)
        self.popup.setWindowTitle(title)
        self.popup.show()


class MainWindowExec:
    def __init__(self):
        app = QtWidgets.QApplication(sys.argv)
        mainwindow = QtWidgets.QMainWindow()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(mainwindow)

        # objects
        self.calc = Calculate()
        self.line_length = CheckInput()
        self.line_diameter = CheckInput()
        self.line_roughness = CheckInput()
        self.liquid_density = CheckInput()
        self.liquid_viscdyn = CheckInput()
        self.liquid_visckin = CheckInput()
        self.flow_velocity = CheckInput()
        self.flow_rate = CheckInput()
        self.messages = Messages()

        self.start_methods()
        mainwindow.show()
        sys.exit(app.exec_())

    def start_methods(self):
        self.ui.Line_Length.editingFinished.connect(self.line_length_start)
        self.ui.Line_Diameter.editingFinished.connect(self.line_diameter_start)
        self.ui.Line_WallRoughness.editingFinished.connect(self.line_wallroughness_start)
        self.ui.Liquid_Density.editingFinished.connect(self.liquid_density_start)
        self.ui.Liquid_ViscDyn.editingFinished.connect(self.liquid_viscdyn_start)
        self.ui.Liquid_ViscKin.editingFinished.connect(self.liquid_visckin_start)
        self.ui.Flow_Velocity.editingFinished.connect(self.flow_velocity_start)
        self.ui.Flow_Rate.editingFinished.connect(self.flow_rate_start)
        self.ui.DynVisKnown.clicked.connect(self.viscosity_known)
        self.ui.KinViscKnown.clicked.connect(self.viscosity_known)
        self.ui.VelocityKnown.clicked.connect(self.flow_or_velocity_known)
        self.ui.FlowRateKnown.clicked.connect(self.flow_or_velocity_known)
        self.ui.actionAbout.triggered.connect(self.help_about)

    def line_length_start(self):
        self.line_length.value_str = self.ui.Line_Length.text()
        self.calc.length = self.line_length.test_input()
        self.calc.length_ok = self.line_length.input_ok
        self.ui.Line_Length.setStyleSheet(self.line_length.style_string)
        self.calc.calculate_start()
        self.output()

    def line_diameter_start(self):
        self.line_diameter.value_str = self.ui.Line_Diameter.text()
        self.calc.diameter = self.line_diameter.test_input()
        self.calc.diameter_ok = self.line_diameter.input_ok
        self.ui.Line_Diameter.setStyleSheet(self.line_diameter.style_string)
        if self.calc.roughness >= self.calc.diameter:
            self.messages.warning('Input inconsistency!', 'Roughness must be smaller than Diameter')
        self.calc.calculate_start()
        self.output()

    def line_wallroughness_start(self):
        self.line_roughness.value_str = self.ui.Line_WallRoughness.text()
        self.calc.roughness = self.line_roughness.test_input()
        self.calc.roughness_ok = self.line_roughness.input_ok
        self.ui.Line_WallRoughness.setStyleSheet(self.line_roughness.style_string)
        if self.calc.roughness >= self.calc.diameter:
            self.messages.warning('Input inconsistency!', 'Roughness must be smaller than Diameter')
        self.calc.calculate_start()
        self.output()

    def liquid_density_start(self):
        self.liquid_density.value_str = self.ui.Liquid_Density.text()
        self.calc.density = self.liquid_density.test_input()
        self.calc.density_ok = self.liquid_density.input_ok
        self.ui.Liquid_Density.setStyleSheet(self.liquid_density.style_string)
        self.calc.calculate_start()
        self.output()

    def liquid_viscdyn_start(self):
        self.liquid_viscdyn.value_str = self.ui.Liquid_ViscDyn.text()
        self.calc.dynamic_viscosity = self.liquid_viscdyn.test_input()
        self.calc.dynamic_viscosity_ok = self.liquid_viscdyn.input_ok
        self.ui.Liquid_ViscDyn.setStyleSheet(self.liquid_viscdyn.style_string)
        self.calc.calculate_start()
        self.output()

    def liquid_visckin_start(self):
        self.liquid_visckin.value_str = self.ui.Liquid_ViscKin.text()
        self.calc.kinematic_viscosity = self.liquid_visckin.test_input()
        self.calc.kinematic_viscosity_ok = self.liquid_visckin.input_ok
        self.ui.Liquid_ViscKin.setStyleSheet(self.liquid_visckin.style_string)
        self.calc.calculate_start()
        self.output()

    def flow_velocity_start(self):
        self.flow_velocity.value_str = self.ui.Flow_Velocity.text()
        self.calc.velocity = self.flow_velocity.test_input()
        self.calc.velocity_ok = self.flow_velocity.input_ok
        self.ui.Flow_Velocity.setStyleSheet(self.flow_velocity.style_string)
        self.calc.calculate_start()
        self.output()

    def flow_rate_start(self):
        self.flow_rate.value_str = self.ui.Flow_Rate.text()
        self.calc.flow_rate = self.flow_rate.test_input()
        self.calc.flow_rate_ok = self.flow_rate.input_ok
        self.ui.Flow_Rate.setStyleSheet(self.flow_rate.style_string)
        self.calc.calculate_start()
        self.output()

    def viscosity_known(self):
        if self.ui.DynVisKnown.isChecked():
            self.ui.Liquid_ViscDyn.setEnabled(True)
            self.ui.Liquid_ViscKin.setEnabled(False)
            self.calc.dynamic_viscosity_active = True
            self.ui.Liquid_ViscDyn.setFocus()
            self.liquid_viscdyn_start()
        else:
            self.ui.Liquid_ViscDyn.setEnabled(False)
            self.ui.Liquid_ViscKin.setEnabled(True)
            self.calc.dynamic_viscosity_active = False
            self.ui.Liquid_ViscKin.setFocus()
            self.liquid_visckin_start()

    def flow_or_velocity_known(self):
        if self.ui.VelocityKnown.isChecked():
            self.ui.Flow_Velocity.setEnabled(True)
            self.ui.Flow_Rate.setEnabled(False)
            self.calc.velocity_active = True
            self.ui.Flow_Velocity.setFocus()
            self.flow_velocity_start()
        else:
            self.ui.Flow_Velocity.setEnabled(False)
            self.ui.Flow_Rate.setEnabled(True)
            self.calc.velocity_active = False
            self.ui.Flow_Rate.setFocus()
            self.flow_rate_start()

    def output(self):
        # format line edit after input
        if self.calc.length_ok:
            self.ui.Line_length_4Calc.setText(f'{self.calc.length:.4e}')
        else:
            self.ui.Line_length_4Calc.setText('Unknown')

        if self.calc.diameter_ok:
            self.ui.Line_Diameter_4Calc.setText(f'{self.calc.diameter:.4e}')
        else:
            self.ui.Line_Diameter_4Calc.setText('Unknown')

        if self.calc.roughness_ok:
            self.ui.Line_WallRoughness_4Calc.setText(f'{self.calc.roughness:.4e}')
        else:
            self.ui.Line_WallRoughness_4Calc.setText('Unknown')

        if self.calc.density_ok:
            self.ui.Liquid_Density_4Calc.setText(f'{self.calc.density:.4e}')
        else:
            self.ui.Liquid_Density_4Calc.setText('Unknown')

        if self.calc.dynamic_viscosity_ok:
            self.ui.Liquid_ViscDyn_4Calc.setText(f'{self.calc.dynamic_viscosity:.4e}')
        else:
            self.ui.Liquid_ViscDyn_4Calc.setText('Unknown')

        if self.calc.kinematic_viscosity_ok:
            self.ui.Liquid_ViscKin_4Calc.setText(f'{self.calc.kinematic_viscosity:.4e}')
        else:
            self.ui.Liquid_ViscKin_4Calc.setText('Unknown')

        if self.calc.velocity_ok:
            self.ui.Flow_Velocity_4Calc.setText(f'{self.calc.velocity:.4e}')
        else:
            self.ui.Flow_Velocity_4Calc.setText('Unknown')

        if self.calc.flow_rate_ok:
            self.ui.Flow_Rate_4Calc.setText(f'{self.calc.flow_rate:.4e}')
        else:
            self.ui.Flow_Rate_4Calc.setText('Unknown')

        # Output fields
        if self.calc.volume_ok:
            self.ui.Output_LineVolume.setText(f'{self.calc.volume:.4e}')
        else:
            self.ui.Output_LineVolume.setText('Unknown')

        if self.calc.reynolds_number_ok:
            self.ui.Output_Reynolds.setText(f'{self.calc.reynolds_number:.4e}')
        else:
            self.ui.Output_Reynolds.setText('Unknown')

        if self.calc.pressure_drop_ok:
            self.ui.Output_PressureDrop.setText(f'{self.calc.pressure_drop:.4e}')
            self.ui.Output_PressureDrop_bar.setText(f'{self.calc.pressure_drop / 100000:.4f}')
        else:
            self.ui.Output_PressureDrop.setText('Unknown')
            self.ui.Output_PressureDrop_bar.setText('Unknown')

        if self.calc.friction_factor_ok:
            self.ui.Output_FrictionFactor.setText(f'{self.calc.friction_factor:.4e}')
        else:
            self.ui.Output_FrictionFactor.setText('Unknown')

        self.ui.Output_FlowRegime.setText(self.calc.flow_regime)
        self.ui.OUtput_ConduitType.setText(self.calc.type_of_conduit)
        self.ui.Output_CalcMethod.setText(self.calc.method)

    def help_about(self):
        # dialog_general.remark
        self.messages.message('Help About', "<html><head/><body><p align=\"center\"><span style=\" "
                                                 "font-size:14pt; font-weight:600;\">"
                                                 "SiPreDroCal</span></p><p><br/></p><p>A "
                                                 "simple pressure drop calculator written in Python</p><p>"
                                                 "Author: Frans van Genesen<br/>Date: June 07, 2021</p><p>"
                                                 "Version 1.0</p><p><br/></p><p>"
                                                 "License: GNU GENERAL PUBLIC LICENSE Version 3</p></body></html>")


if __name__ == "__main__":
    MainWindowExec()
