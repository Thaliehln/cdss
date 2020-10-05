import my_utils
import xls_form_generator as xfg
import calculations as calc
from collections import OrderedDict

####################
# Objects          #
####################

class CDSSObject:
    
    def __init__(self, arg):

        self._attr = OrderedDict()
        if "reference" in arg:
            self._attr['reference'] = arg['reference']
        else:
            self._attr['reference'] = "Q{}".format(my_utils.strHash(bytes(arg['label'], 'utf-8')))
        self._attr['label'] = arg['label']
        for k in ["answers", "appearance", "constr", "default", "hint", "required", "formula", "parameters", "unit"]:
            if k in arg.keys():
                self._attr[k] = arg[k]
            else:
                self._attr[k] = ""

    def getRef(self):
        return self._attr['reference']

    def getLabel(self):
        return self._attr['label']
    
    def getODKQuestion(self):
        return self._odk_question

    def addODKQuestion(self):
        self._attr['type'] = "note"
        self._odk_question = xfg.ODKQuestion(self._attr)

    def addODKSelectOne(self):
        self._attr['required'] = "true()"
        self._odk_question = xfg.ODKSelectOne(self._attr)

    def addODKText(self):
        self._attr['type'] = "text"
        self._attr['required'] = "true()"
        self._odk_question = xfg.ODKQuestion(self._attr)

    def addODKInteger(self):
        self._attr['type'] = "integer"
        self._attr['required'] = "true()"
        self._attr['hint'] = "Enter the value in {}".format(self._attr["unit"])
        self._attr['constr_msg'] = "The entered value must be superior or equal to {} and inferior or equal to {}".format(self._attr['constr'][0],self._attr['constr'][1])
        self._attr['constr'] = ".>={} and .<={}".format(self._attr['constr'][0],self._attr['constr'][1])
        self._odk_question = xfg.ODKQuestion(self._attr)

    def addODKCalculation(self):
        self._attr['type'] = "calculate"
        self._attr['calculation'] = self.getFormula()
        self._odk_question = xfg.ODKQuestion(self._attr)

    def addODKBarcode(self):
        self._attr['type'] = "barcode"
        self._odk_question = xfg.ODKQuestion(self._attr)

    def addODKDate(self):
        self._attr['type'] = "date"
        self._attr['required'] = "true()"
        self._attr['constr_msg'] = "The entered date must be superior or equal to {} and inferior or equal to {}".format(self._attr['constr'][0],self._attr['constr'][1])
        self._attr['constr'] = ".>={} and .<={}".format(self._attr['constr'][0],self._attr['constr'][1])
        self._odk_question = xfg.ODKQuestion(self._attr)

    def addODKRange(self):
        self._attr['type'] = "range"
        self._attr['hint'] = "Move the slider to display the value in {}".format(self._attr["unit"])
        self._attr['required'] = "true()"
        self._attr['parameters'] = "start={};end={};step={}".format(self._attr['parameters'][0],self._attr['parameters'][1], self._attr['parameters'][2])
        self._odk_question = xfg.ODKQuestion(self._attr)

    def getODKQuestion(self):
        return self._odk_question
    
    def getFormula(self):
        return self._attr['formula']

class Demographics(CDSSObject):
    
    def __init__(self, arg):
        arg['reference'] = "DEM{}".format(my_utils.strHash(bytes(arg['label'], 'utf-8')))
        CDSSObject.__init__(self, arg)

class Symptom(CDSSObject):
    
    def __init__(self, arg):
        arg['reference'] = "SYM{}".format(my_utils.strHash(bytes(arg['label'], 'utf-8')))
        CDSSObject.__init__(self, arg)

class ObservedSign(CDSSObject):
    
    def __init__(self, arg):
        arg['reference'] = "OBS{}".format(my_utils.strHash(bytes(arg['label'], 'utf-8')))
        CDSSObject.__init__(self, arg)

class DiagnosisAgreement(CDSSObject):
    
    def __init__(self, arg):
        arg['reference'] = "DAG{}".format(my_utils.strHash(bytes(arg['label'], 'utf-8')))
        CDSSObject.__init__(self, arg)

class ManagementAgreement(CDSSObject):
    
    def __init__(self, arg):
        arg['reference'] = "MAG{}".format(my_utils.strHash(bytes(arg['label'], 'utf-8')))
        CDSSObject.__init__(self, arg)

class TreatmentAgreement(CDSSObject):
    
    def __init__(self, arg):
        arg['reference'] = "TAG{}".format(my_utils.strHash(bytes(arg['label'], 'utf-8')))
        CDSSObject.__init__(self, arg)

class TimeDuration(CDSSObject):
    
    def __init__(self, arg):
        arg['reference'] = "TIM{}".format(my_utils.strHash(bytes(arg['label'], 'utf-8')))
        CDSSObject.__init__(self, arg)
        
class Quantity(CDSSObject):
    
    def __init__(self, arg):
        arg['reference'] = "QUA{}".format(my_utils.strHash(bytes(arg['label'], 'utf-8')))
        CDSSObject.__init__(self, arg)
        
class Measurement(CDSSObject):
    
    def __init__(self, arg):
        arg['reference'] = "MEA{}".format(my_utils.strHash(bytes(arg['label'], 'utf-8')))
        CDSSObject.__init__(self, arg)

class Boolean(CDSSObject):
    
    def __init__(self, arg):
        arg['reference'] = "BOO{}".format(my_utils.strHash(bytes(arg['label'], 'utf-8')))
        self._cond = calc.BooleanCalculation(arg['condition_list'], arg['istrue'], arg['isfalse'])
        arg['formula'] = self._cond.getFormula()
        CDSSObject.__init__(self, arg)

    def getCondition(self):
        return self._cond

    def addCondition(self, cond, logic, g):
        self._cond.addCondition([{'cond':cond.get(),'logic':logic, 'group':g}])
        self._attr['formula'] = self._cond.getFormula()

class Calculation(CDSSObject):
    
    def __init__(self, arg):
        arg['reference'] = "CAL{}".format(my_utils.strHash(bytes(arg['label'], 'utf-8')))
        self._formula = arg['formula']
        CDSSObject.__init__(self, arg)

    def getFormula(self):
        return self._formula

class Score(CDSSObject):
    
    def __init__(self, arg):
        arg['reference'] = "SCO{}".format(my_utils.strHash(bytes(arg['label'], 'utf-8')))
        self._formula = arg['formula']
        CDSSObject.__init__(self, arg)

class Research(CDSSObject):
    
    def __init__(self, arg):
        arg['reference'] = "RES{}".format(my_utils.strHash(bytes(arg['label'], 'utf-8')))
        CDSSObject.__init__(self, arg)

class PII(CDSSObject):
    
    def __init__(self, arg):
        arg['reference'] = "PII{}".format(my_utils.strHash(bytes(arg['label'], 'utf-8')))
        CDSSObject.__init__(self, arg)

#############
# Diagnosis #
#############
    
class Diagnosis:
    
    def __init__(self, lbl, severity, answers):
        self._reference = "DIA{}".format(my_utils.strHash(bytes(lbl, 'utf-8')))
        self._label = lbl
        self._severity = severity
        
        self._criterion = ""
        self._agreement_asw = answers.getItem("AGREEMENT")
        self._agreement = None
        self._agreement_dict = OrderedDict()
        
        self._calculations = OrderedDict()
        self._questions = OrderedDict()
        
    def getLabel(self):
        return self._label

    def getRef(self):
        return self._reference

    def getSeverity(self):
        return self._severity

    def getDiagnosisAgreement(self):
        return self._agreement

    def getCalculations(self):
        return self._calculations

    # Add criterion leading to the diagnosis
    def addInclusionCriterion(self, mod_lbl, q, asw, logic="or", g=0):
        try:
            cond = calc.EqualAnswerCond(q, asw)
        except:
            cond = calc.EqualCalculationCond(q, asw)
        if mod_lbl not in self._calculations.keys():
            old_cond = self._calculations[list(self._calculations.keys())[-1]].getCondition()
            self._calculations[mod_lbl] = None
            self.addCalculation(mod_lbl, old_cond)
        self.addCalculation(mod_lbl, cond, logic, g)
        self._criterion = "{0}\n{1} {2} = ${{{3}}}".format(self._criterion, logic.upper(), q.getLabel().split(" - ")[0], q.getRef())
        self.updateAgreement()

    # Add diagnosis excluding the diagnosis
    def addExclusionDiagnosis(self, mod_lbl, q, logic="and", g=1):
        cond  = calc.EqualCalculationCond(q, "0")
        if mod_lbl not in self._calculations.keys():
            old_cond = self._calculations[list(self._calculations.keys())[-1]].getRef()
            self._calculations[mod_lbl] = None
            self.addCalculation(mod_lbl, calc.Condition("${{{}}}=1".format(old_cond)))
        self.addCalculation(mod_lbl, cond, logic, g)
        self._criterion = "{0}\n{1} NO {2} = ${{{3}}}".format(self._criterion, logic.upper(), q.getLabel().split(" - ")[0], q.getRef())
        self.updateAgreement()

    def updateAgreement(self):
        self._agreement_dict["hint"] = self._criterion
        self._agreement = DiagnosisAgreement(self._agreement_dict)
        self._agreement.addODKSelectOne()
        k = list(self._calculations.keys())[-1]
        self._agreement.getODKQuestion().addTopConditionCalculation(self._calculations[k].getODKQuestion(),"1")

    def addCalculation(self, mod_lbl, cond, logic="or", g=0):

        lbl = "{} - {}".format(self._label, mod_lbl)
        if self._calculations[mod_lbl] is None:
            calc_d = {"type":"boolean",
                "label":lbl,
                "condition_list":[{'cond':cond.get()}],
                "istrue":1,
                "isfalse":0}
            self._calculations[mod_lbl] = Boolean(calc_d)
            self._calculations[mod_lbl].addODKCalculation()
        else:
            self._calculations[mod_lbl].addCondition(cond, logic, g)
            self._calculations[mod_lbl].addODKCalculation()

    def addNewCalculation(self, mod_lbl, q, asw):

        # Create new calculation
        try:
            cond = calc.EqualAnswerCond(q, asw)
        except:
            cond = calc.EqualCalculationCond(q, asw)
        self._calculations[mod_lbl] = None
        self.addCalculation(mod_lbl, cond)

        # Create Diagnosis agreement question
        self._criterion = "{0} = ${{{1}}}".format(q.getLabel().split(" - ")[0], q.getRef())
        if self._severity == "mild":
            color = "#008000"
        elif self._severity == "moderate":
            color = "#ffd700"
        elif self._severity == "severe":
            color = "#ff8080"
        else:
            color = "#808080"
        self._agreement_dict = {"label":'<span style="color:{}">{}</span>'.format(color, self._label), "answers":self._agreement_asw, "hint":self._criterion}
        self.updateAgreement()

##############
# Management #
##############
        
class Management:
    
    def __init__(self, lbl, answers):
        self._reference = "MGT{}".format(my_utils.strHash(bytes(lbl, 'utf-8')))
        self._label = lbl
        
        self._criterion = ""
        self._agreement_asw = answers.getItem("POSSIBLE")
        self._agreement = None
        self._agreement_dict = OrderedDict()
        
        self._calculations = OrderedDict()
        self._questions = OrderedDict()
        
    def getLabel(self):
        return self._label

    def getRef(self):
        return self._reference

    def getManagementAgreement(self):
        return self._agreement

    def getCalculations(self):
        return self._calculations

    # Add diagnosis leading to the management
    def addInclusionCriterion(self, mod_lbl, q, logic="or", g=0):
        cond = calc.EqualCalculationCond(q, "1")
        if mod_lbl not in self._calculations.keys():
            old_cond = self._calculations[list(self._calculations.keys())[-1]].getCondition()
            self._calculations[mod_lbl] = None
            self.addCalculation(mod_lbl, old_cond)
        self.addCalculation(mod_lbl, cond, logic, g)
        self._criterion = "{0}\n{1} {2} = ${{{3}}}".format(self._criterion, logic.upper(), q.getLabel().split(" - ")[0], q.getRef())
        self.updateAgreement()

    # Add diagnosis excluding the management
    def addExclusionDiagnosis(self, mod_lbl, q, logic="and", g=1):
        cond  = calc.EqualCalculationCond(q, "0")
        if mod_lbl not in self._calculations.keys():
            old_cond = self._calculations[list(self._calculations.keys())[-1]].getRef()
            self._calculations[mod_lbl] = None
            self.addCalculation(mod_lbl, calc.Condition("${{{}}}=1".format(old_cond)))
        self.addCalculation(mod_lbl, cond, logic, g)
        self._criterion = "{0}\n{1} NO {2} = ${{{3}}}".format(self._criterion, logic.upper(), q.getLabel().split(" - ")[0], q.getRef())
        self.updateAgreement()

    def addCalculation(self, mod_lbl, cond, logic="or", g=0):

        lbl = "{} - {}".format(self._label, mod_lbl)
        if self._calculations[mod_lbl] is None:
            calc_d = {"type":"boolean",
                "label":lbl,
                "condition_list":[{'cond':cond.get()}],
                "istrue":1,
                "isfalse":0}
            self._calculations[mod_lbl] = Boolean(calc_d)
            self._calculations[mod_lbl].addODKCalculation()
        else:
            self._calculations[mod_lbl].addCondition(cond, logic, g)
            self._calculations[mod_lbl].addODKCalculation()

    def updateAgreement(self):
        self._agreement_dict["hint"] = self._criterion
        self._agreement = ManagementAgreement(self._agreement_dict)
        self._agreement.addODKSelectOne()
        k = list(self._calculations.keys())[-1]
        self._agreement.getODKQuestion().addTopConditionCalculation(self._calculations[k].getODKQuestion(),"1")

    def addNewCalculation(self, mod_lbl, q, asw):

        # Create new calculation
        cond = calc.EqualCalculationCond(q, asw)
        self._calculations[mod_lbl] = None
        self.addCalculation(mod_lbl, cond)

        # Create Management agreement question
        self._criterion = "{0} = ${{{1}}}".format(q.getLabel().split(" - ")[0], q.getRef())
        self._agreement_dict = {"label":self._label, "answers":self._agreement_asw, "hint":self._criterion}
        self.updateAgreement()

#############
# Treatment #
#############
        
class Treatment:

    def __init__(self, lbl, answers):
        self._reference = "TRT{}".format(my_utils.strHash(bytes(lbl, 'utf-8')))
        self._label = lbl
        
        self._criterion = ""
        self._agreement_asw = answers.getItem("POSSIBLE")
        self._agreement = None
        self._agreement_dict = OrderedDict()
        
        self._calculations = OrderedDict()
        self._questions = OrderedDict()
        
    def getLabel(self):
        return self._label

    def getRef(self):
        return self._reference

    def getAgreement(self):
        return self._agreement

    def getCalculations(self):
        return self._calculations

    # Add diagnosis leading to the treatment
    def addInclusionCriterion(self, mod_lbl, q, logic="or", g=0):
        cond = calc.EqualCalculationCond(q, "1")
        if mod_lbl not in self._calculations.keys():
            old_cond = self._calculations[list(self._calculations.keys())[-1]].getCondition()
            self._calculations[mod_lbl] = None
            self.addCalculation(mod_lbl, old_cond)
        self.addCalculation(mod_lbl, cond, logic, g)
        self._criterion = "{0}\n{1} {2} = ${{{3}}}".format(self._criterion, logic.upper(), q.getLabel().split(" - ")[0], q.getRef())
        self.updateAgreement()

    # Add diagnosis excluding the treatment
    def addExclusionDiagnosis(self, mod_lbl, q, logic="and", g=1):
        cond  = calc.EqualCalculationCond(q, "0")
        if mod_lbl not in self._calculations.keys():
            old_cond = self._calculations[list(self._calculations.keys())[-1]].getRef()
            self._calculations[mod_lbl] = None
            self.addCalculation(mod_lbl, calc.Condition("${{{}}}=1".format(old_cond)))
        self.addCalculation(mod_lbl, cond, logic, g)
        self._criterion = "{0}\n{1} NO {2} = ${{{3}}}".format(self._criterion, logic.upper(), q.getLabel().split(" - ")[0], q.getRef())
        self.updateAgreement()

    def addCalculation(self, mod_lbl, cond, logic="or", g=0):

        lbl = "{} - {}".format(self._label, mod_lbl)
        if self._calculations[mod_lbl] is None:
            calc_d = {"type":"boolean",
                "label":lbl,
                "condition_list":[{'cond':cond.get()}],
                "istrue":1,
                "isfalse":0}
            self._calculations[mod_lbl] = Boolean(calc_d)
            self._calculations[mod_lbl].addODKCalculation()
        else:
            self._calculations[mod_lbl].addCondition(cond, logic, g)
            self._calculations[mod_lbl].addODKCalculation()

    def updateAgreement(self):
        self._agreement_dict["hint"] = self._criterion
        self._agreement = TreatmentAgreement(self._agreement_dict)
        self._agreement.addODKSelectOne()
        k = list(self._calculations.keys())[-1]
        self._agreement.getODKQuestion().addTopConditionCalculation(self._calculations[k].getODKQuestion(),"1")

    def addNewCalculation(self, mod_lbl, q, asw):

        # Create new calculation
        cond = calc.EqualCalculationCond(q, asw)
        self._calculations[mod_lbl] = None
        self.addCalculation(mod_lbl, cond)

        # Create Management agreement question
        self._criterion = "{0} = ${{{1}}}".format(q.getLabel().split(" - ")[0], q.getRef())
        self._agreement_dict = {"label":self._label, "answers":self._agreement_asw, "hint":self._criterion}
        self.updateAgreement()

########
# Drug #
########
        
class Drug(Treatment):
    
    def __init__(self, lbl, answers):
        self._reference = "DRG{}".format(my_utils.strHash(bytes(lbl, 'utf-8')))
        self._agreement_asw = answers.getItem("AVAILABLE")