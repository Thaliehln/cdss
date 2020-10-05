import my_utils
import pandas as pd
import xls_form_generator as xfg
import clinical_objects as cobj
import calculations as calc

class ClinicalAlgorithm:

    def __init__(self):
        self._welcome_screen         = None
        self._modules                = dict()
        self._submodules             = dict()
        self._header                 = dict()
        self._answers                = AnswerDict()
        self._questions              = QuestionDict()
        self._diagnoses              = DiagnosisDict()
        self._managements            = ManagementDict()
        self._treatments             = TreatmentDict()
        self._drugs                  = TreatmentDict()

    # ODK export
    def initODKExport(self, form_title, form_id, version, languages, def_language):
        self._odk = dict()
        self._odk["survey_df"], self._odk["choices_df"], self._odk["settings_df"] = xfg.initialiseXLSForm(form_title, form_id, version, languages, def_language)
        # Meta data
        row = pd.DataFrame([["today","today","","","","","","","","","","","","","","","","","","","","","",""],
                            ["start","start","","","","","","","","","","","","","","","","","","","","","",""],
                            ["end","end","","","","","","","","","","","","","","","","","","","","","",""],
                            ["deviceid","deviceid","","","","","","","","","","","","","","","","","","","","","",""],
                            ["audit","audit","","","","","","","","","","","","","","","","","","","","","","track-changes-reasons=on-form-edit track-changes=true"]], columns=self._odk["survey_df"].columns.values)
        self._odk["survey_df"] = self._odk["survey_df"].append(row)

    def getODKExport(self):
        return self._odk

    def ODKExport(self, filename):
        self._odk['survey_df'] = self._welcome_screen.export(self._odk['survey_df'])
        for key, val in self.getModules().items():
            print(key)
            print(type(val))
            self._odk['survey_df'] = val.export(self._odk['survey_df'], key, self._questions, self._diagnoses, self._managements, self._treatments)
        xfg.writeXLSForm(filename, self._odk['survey_df'], self._odk['choices_df'], self._odk['settings_df'])

    # Welcome screen
    def addWelcomeScreen(self, arg):
        self._welcome_screen = AppWelcomeScreen(arg, "timci1.png")
    
    # Answers
    def addAnswers(self, arg):
        self.getAnswers().addAnswers(arg)
        self.getODKExport()["choices_df"] = self.getAnswers().ODKExport(self.getODKExport()["choices_df"])

    def getAnswer(self, lbl):
        return self._answers.get()[lbl].getAnswers()
    
    def getAnswers(self):
        return self._answers

    # Questions
    def addQuestions(self, arg):
        self._questions.addQuestions(arg, self._answers)

    def getQuestion(self, lbl):
        return self._questions.get()[lbl]
    
    def getQuestions(self):
        return self._questions

    def addQuestionTopConditions(self, arg):
        for val in arg:
            if "logic" in val.keys() and "group" in val.keys():
                self._questions.getItem(val["child"]).addTopConditionQuestion(self._questions.getItem(val['parent']), val['answer'], val['logic'], val['group'])
            else:
                self._questions.getItem(val["child"]).addTopConditionQuestion(self._questions.getItem(val['parent']), val['answer'])

    def addManagementTopConditions(self, arg):
        for val in arg:
            if "logic" in val.keys() and "group" in val.keys():
                self._managements.getItem(val["child"]).getManagementAgreement().getODKQuestion().addTopConditionQuestion(self._managements.getItem(val['parent']).getManagementAgreement().getODKQuestion(), val['answer'], val['logic'], val['group'])
            else:
                self._managements.getItem(val["child"]).getManagementAgreement().getODKQuestion().addTopConditionQuestion(self._managements.getItem(val['parent']).getManagementAgreement().getODKQuestion(), val['answer'])


    def addRegistrationQuestions(self):
        t = "pii"
        free_text = [
            {"label":"First name", "type":t, "odk_type":"free_text"},
            {"label":"Last name", "type":t, "odk_type":"free_text"},
        ]
        self.addQuestions(free_text)

        t = "research"
        non_clinical = [
            {"label":"Does the child have a study ID?", "type":t, "odk_type":"select_one", "asw_lbl":"YESNO"},
            {"label":"Please scan the child's study ID", "type":t, "odk_type":"barcode"},
            {"label":"If QR code scanning is not possible, please manually enter the child's study ID", "type":t, "odk_type":"free_text"}
        ]
        self.addQuestions(non_clinical)

        t = "demographics"
        demographics = [
            {"label":"Exact date of birth known?", "type":t, "odk_type":"select_one", "asw_lbl":"YESNO"},
            {"label":"Year and month of birth known?", "type":t, "odk_type":"select_one", "asw_lbl":"YESNO"},
            {"label":"Date of birth", "type":t, "odk_type":"date", "appearance":"", "constr":["date('2000-01-01')","today()"]},
            {"label":"Year and month of birth", "type":t, "odk_type":"date", "appearance":"month-year", "constr":["date('2000-01-01')","today()"]},
            {"label":"Age category", "type":t, "odk_type":"select_one", "asw_lbl":"MCAT"},
            {"label":"Age in months", "type":t, "odk_type":"time duration", "unit":"months","constr":[0,59], "hint":"1 year = 12 months; 2 years = 24 months; 3 years = 36 months"},
            {"label":"Age in days", "type":t, "odk_type":"time duration", "unit":"days","constr":[0,59]},
            {"label":"Sex", "type":t, "odk_type":"select_one", "asw_lbl":"SEX"}
        ]
        self.addQuestions(demographics)

        t = "calculation"
        calculations = [
            {
                "label":"Year from year and month of birth",
                "type":t,
                "formula":"if(${{{0}}}!='', format-date(${{{0}}},'%Y'), '')".format(self._questions.getItem("Year and month of birth").getRef())},
            {
                "label":"Month from year and month of birth",
                "type":t,
                "formula":"if(${{{0}}}!='', format-date(${{{0}}},'%m'), '')".format(self._questions.getItem("Year and month of birth").getRef())}
        ]
        self.addQuestions(calculations)
        calculations = [    
            {
                "label":"Calculated date of birth from year and month of birth",
                "type":t,
                "formula":"if(${{{0}}}!='', concat(${{{0}}},'-', ${{{1}}}, '-28'), '')".format(
                    self._questions.getItem("Year from year and month of birth").getRef(),
                    self._questions.getItem("Month from year and month of birth").getRef())}
        ]
        self.addQuestions(calculations)
        calculations = [
            {
                "label":"Calculated age in months",
                "type":t,
                "formula":"if(${{{0}}}!='', ${{{0}}}, if(${{{1}}}!='', int((today() - date(${{{1}}})) div 30.44), if(${{{2}}}!='', int((today() - date(${{{2}}})) div 30.44), 'Test')))".format(
                    self._questions.getItem("Age in months").getRef(),
                    self._questions.getItem("Date of birth").getRef(),
                    self._questions.getItem("Calculated date of birth from year and month of birth").getRef()
                    )},
            {
                "label":"Calculated age in days",
                "type":t,
                "formula":"if(${{{0}}}!='', ${{{0}}}, if(${{{1}}}!='', today() - date(${{{1}}}), 'Test'))".format(
                    self._questions.getItem("Age in months").getRef(),
                    self._questions.getItem("Date of birth").getRef(),
                    )}
        ]
        self.addQuestions(calculations)
        calculations = [
            {
                "label":"Header",
                "type":t,
                "formula":"concat(${{{0}}}, '&nbsp;', ${{{1}}}, ' - ', jr:choice-name(${{{2}}}, '${{{2}}}'), '<br/>', ${{{3}}}, ' months')".format(
                    self._questions.getItem("First name").getRef(),
                    self._questions.getItem("Last name").getRef(),
                    self._questions.getItem("Sex").getRef(),
                    self._questions.getItem("Calculated age in months").getRef())}
        ]
        self.addQuestions(calculations)
        self._header["Registration"] = "${{{0}}}".format(self._questions.getItem("Header").getRef())

    # Add header
    def addHeader(self):
        calculations = [
            {
                "label":"CHeader",
                "type":"calculation",
                "formula":"concat(${{{0}}}, ' - ', ${{{1}}}, ' kg')".format(
                    self._questions.getItem("Header").getRef(),
                    self._questions.getItem("Weight").getRef())}
        ]
        self.addQuestions(calculations)
        self._header["Consultation"] = "${{{0}}}".format(self._questions.getItem("CHeader").getRef())

    def getHeader(self):
        return self._header

    # Diagnoses
    def addDiagnoses(self, diagnoses, severity):
        self._diagnoses.addDiagnoses(diagnoses, severity, self._answers)

    def addDiagnosisCriteria(self, mod_lbl, arg):
        for val in arg:
            if (not bool(self._diagnoses.getItem(val["diagnosis"]).getCalculations())) or (mod_lbl not in self._diagnoses.getItem(val["diagnosis"]).getCalculations().keys()):
                self._diagnoses.getItem(val["diagnosis"]).addNewCalculation(mod_lbl, self._questions.getItem(val['criterion']), val['answer'])
            else:
                self._diagnoses.getItem(val["diagnosis"]).addInclusionCriterion(mod_lbl, self._questions.getItem(val['criterion']), val['answer'], val['logic'], val['group'])
    
    def addExcludingDiagnosis(self, mod_lbl, arg):
        for val in arg:
            if not bool(self._diagnoses.getItem(val["diagnosis"]).getCalculations()):
                self._diagnoses.getItem(val["diagnosis"]).addNewCalculation(mod_lbl, self._diagnoses.getItem(val['excluding_diagnosis']), 0)
            else:
                k = list(self._diagnoses.getItem(val['excluding_diagnosis']).getCalculations().keys())[-1]
                self._diagnoses.getItem(val["diagnosis"]).addExclusionDiagnosis(mod_lbl, self._diagnoses.getItem(val['excluding_diagnosis']).getCalculations()[k], val['logic'], val['group'])

    def addIncludingDiagnosis(self, mod_lbl, arg):
        for val in arg:
            if (not bool(self._diagnoses.getItem(val["diagnosis"]).getCalculations())) or (mod_lbl not in self._diagnoses.getItem(val["diagnosis"]).getCalculations().keys()):
                self._diagnoses.getItem(val["diagnosis"]).addNewCalculation(mod_lbl, self._diagnoses.getItem(val['including_diagnosis']), 1)
            else:
                k = list(self._diagnoses.getItem(val['including_diagnosis']).getCalculations().keys())[-1]
                self._diagnoses.getItem(val["diagnosis"]).addInclusionCriterion(mod_lbl, self._diagnoses.getItem(val['including_diagnosis']).getCalculations()[k], 1, val['logic'], val['group'])

    def getDiagnosis(self, lbl):
        return self._diagnoses.get()[lbl]
    
    def getDiagnoses(self):
        return self._diagnoses
    
    def printDiagnoses(self):
        for key, val in self._diagnoses.get().items():
            print(key, val.getSeverity(), val)

    # Management
    def addManagements(self, managements):
        self._managements.addManagements(managements, self._answers)

    def addDiagnosisManagement(self, mod_lbl, arg):
        for val in arg:
            if (not bool(self._managements.getItem(val["mgt"]).getCalculations())) or (mod_lbl not in self._managements.getItem(val["mgt"]).getCalculations().keys()):
                self._managements.getItem(val["mgt"]).addNewCalculation(mod_lbl, self._diagnoses.getItem(val['diagnosis']).getDiagnosisAgreement(), "1")
            else:
                self._managements.getItem(val["mgt"]).addInclusionCriterion(mod_lbl, self._diagnoses.getItem(val['diagnosis']).getDiagnosisAgreement())

    def addExcludingManagement(self, mod_lbl, arg):
        for val in arg:
            if not bool(self._managements.getItem(val["mgt"]).getCalculations()):
                self._managements.getItem(val["mgt"]).addNewCalculation(mod_lbl, self._managements.getItem(val['excluding_mgt']), 0)
            else:
                k = list(self._managements.getItem(val['excluding_mgt']).getCalculations().keys())[-1]
                self._managements.getItem(val["mgt"]).addExclusionDiagnosis(mod_lbl, self._managements.getItem(val['excluding_mgt']).getCalculations()[k], val['logic'], val['group'])

    def addIncludingManagement(self, mod_lbl, arg):
        for val in arg:
            if (not bool(self._managements.getItem(val["mgt"]).getCalculations())) or (mod_lbl not in self._managements.getItem(val["mgt"]).getCalculations().keys()):
                self._managements.getItem(val["mgt"]).addNewCalculation(mod_lbl, self._managements.getItem(val['including_mgt']), 1)
            else:
                k = list(self._managements.getItem(val['including_mgt']).getCalculations().keys())[-1]
                self._managements.getItem(val["mgt"]).addInclusionCriterion(mod_lbl, self._managements.getItem(val['including_mgt']).getCalculations()[k], 1, val['logic'], val['group'])
    
    def getManagement(self, lbl):
        return self._managements.get()[lbl]
    
    def getManagements(self):
        return self._managements
    
    def printManagements(self):
        for key, val in self._managements.get().items():
            print(key, val)

    # Treatments
    def addTreatments(self, arg):
        self._treatments.addTreatments(arg, self._answers)

    def addTreatment2Diagnosis(self, mod_lbl, arg):
        for val in arg:
            if (not bool(self._treatments.getItem(val["treatment"]).getCalculations())) or (mod_lbl not in self._treatments.getItem(val["treatment"]).getCalculations().keys()):
                self._treatments.getItem(val["treatment"]).addNewCalculation(mod_lbl, self._diagnoses.getItem(val['diagnosis']).getDiagnosisAgreement(), "1")
            else:
                self._treatments.getItem(val["treatment"]).addInclusionCriterion(mod_lbl, self._diagnoses.getItem(val['diagnosis']).getDiagnosisAgreement())


    def addTreatment2Criterion(self, mod_lbl, arg):
        for val in arg:
            if (not bool(self._treatments.getItem(val["treatment"]).getCalculations())) or (mod_lbl not in self._treatments.getItem(val["treatment"]).getCalculations().keys()):
                self._treatments.getItem(val["treatment"]).addNewCalculation(mod_lbl, self._questions.getItem(val['criterion']), val['answer'])
            else:
                self._treatments.getItem(val["treatment"]).addInclusionCriterion(mod_lbl, self._questions.getItem(val['criterion']), val['answer'], val['logic'], val['group'])

    def getTreatment(self, lbl):
        return self._treatments.get()[lbl]
    
    def getTreatments(self):
        return self._treatments
    
    def printTreatments(self):
        for key, val in self._treatments.get().items():
            print(key, val)

    def getDrugs(self):
        return self._drugs

    # Modules
    def getModule(self, lbl):
        return self._modules[lbl]
    
    def getModules(self):
        return self._modules

    def getSubModule(self, lbl):
        return self._submodules[lbl]
    
    def getSubModules(self):
        return self._submodules

    def addRegistrationModule(self, lbl):
        self._modules[lbl] = RegistrationModule(lbl, self._answers)

        top_conditions = [
            {
                "child":"Please scan the child's study ID",
                "parent":"Does the child have a study ID?",
                "answer":"Yes"},
            {
                "child":"If QR code scanning is not possible, please manually enter the child's study ID",
                "parent":"Does the child have a study ID?",
                "answer":"Yes"},
            {
                "child":"Date of birth",
                "parent":"Exact date of birth known?",
                "answer":"Yes"},
            {
                "child":"Year and month of birth known?",
                "parent":"Exact date of birth known?",
                "answer":"No"},
            {
                "child":"Year and month of birth",
                "parent":"Year and month of birth known?",
                "answer":"Yes"},
            {
                "child":"Age category",
                "parent":"Year and month of birth known?",
                "answer":"No"},
            {
                "child":"Age in days",
                "parent":"Age category",
                "answer":"2 months and less"},
            {
                "child":"Age in months",
                "parent":"Age category",
                "answer":"2-59 months"}
        ]
        self.addQuestionTopConditions(top_conditions)

        registration_calculations = [
            "Year from year and month of birth",
            "Month from year and month of birth",
            "Calculated date of birth from year and month of birth",
            "Calculated age in months",
            "Young infant",
            "Header"]
        self._modules[lbl].addCalculationSubModule()
        for k in registration_calculations:
            self._modules[lbl].getCalculationSubModules()[-1].addQuestion(k)

    def addModule(self, lbl, h=""):
        self._modules[lbl] = ConsultationModule(lbl, h)

    def addModuleTopConditions(self, arg):
        for val in arg:
            if "logic" in val.keys() and "group" in val.keys():
                self.getModule(val["child"]).addTopConditionQuestion(self._questions.getItem(val['parent']), val['answer'], val['logic'], val['group'])
            else:
                self.getModule(val["child"]).addTopConditionQuestion(self._questions.getItem(val['parent']), val['answer'])

    def addModuleTopConditionDiagnoses(self, arg):
        for val in arg:
            if "logic" in val.keys() and "group" in val.keys():
                self.getModule(val["child"]).addTopConditionDiagnosis(self._diagnoses.getItem(val['parent']), val['answer'], val['logic'], val['group'])
            else:
                self.getModule(val["child"]).addTopConditionDiagnosis(self._diagnoses.getItem(val['parent']), val['answer'])

    def addSubModule(self, submodule_lbl, parent_lbl):
        self._submodules[submodule_lbl] = SubModule(submodule_lbl, self._modules[parent_lbl])
        self._modules[parent_lbl].addSubModule(self._submodules[submodule_lbl])

    def addSubModuleTopConditions(self, lbl, arg):
        for val in arg:
            if "logic" in val.keys() and "group" in val.keys():
                self._submodules[lbl].addTopConditionQuestion(self._questions.getItem(val['parent']), val['answer'], val['logic'], val['group'])
            else:
                self._submodules[lbl].addTopConditionQuestion(self._questions.getItem(val['parent']), val['answer'])

    def addTableSubModule(self, submodule_lbl, parent_lbl):
        self._submodules[submodule_lbl] = TableSubModule(submodule_lbl, self._modules[parent_lbl])
        self._modules[parent_lbl].addSubModule(self._submodules[submodule_lbl])

    def addDiagnosisModule(self, lbl):
        self._modules[lbl] = Module(lbl)
        submodule_lbl = "{} agreement table".format(lbl)
        self._submodules[submodule_lbl] = DiagnosisAgreementSubModule("Recommended diagnoses", self._modules[lbl])
        for k in self.getDiagnoses().get().keys():
            self._submodules[submodule_lbl].addQuestion(k)
        self._modules[lbl].addSubModule(self._submodules[submodule_lbl])

    def addManagementModule(self, lbl):
        self._modules[lbl] = Module(lbl)
        submodule_lbl = "{} agreement table".format(lbl)
        self._submodules[submodule_lbl] = ManagementAgreementSubModule("Recommended management", self._modules[lbl])
        for k in self.getManagements().get().keys():
            self._submodules[submodule_lbl].addQuestion(k)
        self._modules[lbl].addSubModule(self._submodules[submodule_lbl])

    def addTreatmentModule(self, lbl):
        self._modules[lbl] = Module(lbl)
        submodule_lbl = "{} agreement table".format(lbl)
        self._submodules[submodule_lbl] = TreatmentAgreementSubModule("Recommended treatment steps", self._modules[lbl])
        for k in self.getTreatments().get().keys():
            self._submodules[submodule_lbl].addQuestion(k)
        self._modules[lbl].addSubModule(self._submodules[submodule_lbl])

    def addDrugModule(self, lbl):
        self._modules[lbl] = Module(lbl)
        submodule_lbl = "{} agreement table".format(lbl)
        self._submodules[submodule_lbl] = TreatmentAgreementSubModule("Recommended drugs", self._modules[lbl])
        for k in self.getDrugs().get().keys():
            self._submodules[submodule_lbl].addQuestion(k)
        self._modules[lbl].addSubModule(self._submodules[submodule_lbl])

    def addDiagnosisCalculations(self, lbl):
        self._modules[lbl] = DiagnosisCalculationModule(lbl)  
    
    def addManagementCalculations(self, lbl):
        self._modules[lbl] = ManagementCalculationModule(lbl)

    def addTreatmentCalculations(self, lbl):
        self._modules[lbl] = TreatmentCalculationModule(lbl)

class AppWelcomeScreen:
    
    def __init__(self, titles, img):
        self._reference = "APP001"
        self._welcome_screen = xfg.ODKWelcomeScreen(self._reference, titles, img)

    def getLabel(self):
        return self._label

    def export(self, df):
        df = self._welcome_screen.export(df)
        row = pd.DataFrame([["","","","","","","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        return df

class Module:
    
    def __init__(self, lbl, header=""):
        self._reference = my_utils.strHash(bytes(lbl, 'utf-8'))
        self._label = lbl
        self._hint = header
        self._cond = ""
        self._media = "timci_bg.png"
        self._title = xfg.ODKH1Title("", self._label, "left", "#495d83", self._hint, self._media)
        self._question_list = []
        self._submodule_list = []
        self._calc_submodule_list = []
        self._calculation_submodule = None
        self._complex_conditions = None

    def getLabel(self):
        return self._label

    def addSubModule(self, module):
        self._submodule_list.append(module)

    def getSubModules(self):
        return self._submodule_list

    def addCalculationSubModule(self):
        self._calc_submodule_list.append(CalculationModule(self._label))

    def addDiagnosisCalculationSubModule(self):
        self._calc_submodule_list.append(DiagnosisCalculationModule(self._label))

    def getCalculationSubModules(self):
        return self._calc_submodule_list

    def addQuestion(self, q):
        self._question_list.append(q)

    def addDiagnosisCalculationQuestion(self, q):
        if self._label in q.getCalculations().keys():
            self._question_list.append(q.getCalculations()[self._label])
        
    def addTopConditionQuestion(self, q, asw, logic="or", group=0):
        cond = calc.EqualAnswerCond(q, asw)
        if self._complex_conditions is None:
            self._complex_conditions = calc.ComplexConditions([{'cond':cond.get(),'logic':logic, 'group':group}])
        else:
            self._complex_conditions.addCondition([{'cond':cond.get(),'logic':logic, 'group':group}])
        self._cond = self._complex_conditions.getConditionStr()

    def addTopConditionCalculation(self, q, asw, logic="or", group=0):
        cond = calc.EqualCalculationCond(q, asw)
        if self._complex_conditions is None:
            self._complex_conditions = calc.ComplexConditions([{'cond':cond.get(),'logic':logic, 'group':group}])
        else:
            self._complex_conditions.addCondition([{'cond':cond.get(),'logic':logic, 'group':group}])
        self._cond = self._complex_conditions.getConditionStr()

    def addTopConditionDiagnosis(self, q, asw, logic="or", group=0):
        k = list(q.getCalculations().keys())[-1]
        cond = calc.EqualCalculationCond(q.getCalculations()[k], asw)
        if self._complex_conditions is None:
            self._complex_conditions = calc.ComplexConditions([{'cond':cond.get(),'logic':logic, 'group':group}])
        else:
            self._complex_conditions.addCondition([{'cond':cond.get(),'logic':logic, 'group':group}])
        self._cond = self._complex_conditions.getConditionStr()
    
    def getTopCondition(self):
        return self._cond

    def printQuestionList(self):
        for q in self._question_list:
            print(q)

    def export(self, df, key, questions, diagnoses, managements, treatments, appearance="field-list"):
        row = pd.DataFrame([["begin_group","MOD{}".format(self._reference),self._label,"","",appearance,self._cond,"","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        df = self._title.export(df)
        for q in self._question_list:
            df = questions.get()[q].export(df)
        for sm in self._submodule_list:
            if type(sm) is DiagnosisAgreementSubModule:
                df = sm.export(df, diagnoses)
            elif type(sm) is ManagementAgreementSubModule:
                df = sm.export(df, managements)
            elif type(sm) is TreatmentAgreementSubModule:
                df = sm.export(df, treatments)
            else:
                df = sm.export(df, questions)
        row = pd.DataFrame([["end_group","","","","","","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        row = pd.DataFrame([["","","","","","","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        for csm in self._calc_submodule_list:
            if type(csm) is CalculationModule:
                df = csm.export(df, "", questions, diagnoses, managements, treatments)
            elif type(csm) is DiagnosisCalculationModule:
                df = csm.export(df, self.getLabel(), questions, diagnoses, managements, treatments)
        row = pd.DataFrame([["","","","","","","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        return df

class SubModule(Module):

    def __init__(self, lbl, parent):
        Module.__init__(self, lbl)
        self._reference = my_utils.strHash(bytes("{} {}".format(parent, lbl), 'utf-8'))
        self._parent = parent

    def export(self, df, questions):
        for q in self._question_list:
            df = questions.get()[q].export(df)
        return df

class DiagnosisCalculationSubModule(SubModule):
    
    def __init__(self, lbl, parent):
        SubModule.__init__(self, lbl, parent)

    def export(self, df, diagnoses):
        for q in self._question_list:
            cdict = diagnoses.get()[q].getCalculations()
            for calc in cdict.values():
                if calc is not None:
                    if type(calc) is cobj.Boolean:
                        df = calc.getODKQuestion().export(df)
                    else:
                        df = calc.export(df)
        return df

class TableSubModule(SubModule):

    def __init__(self, lbl, parent):
        SubModule.__init__(self, lbl, parent)
        self._title = xfg.ODKH2Title("", self._label, "left", "#ed8a78", self._hint, self._media)

    def export(self, df, questions):
        row = pd.DataFrame([["begin_group","TAB{}".format(self._reference),self._title.getLabel(),"","","table-list","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        for q in self._question_list:
            df = questions.get()[q].export(df)
        row = pd.DataFrame([["end_group","","","","","","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        return df

class RepeatSubModule(SubModule):

    def __init__(self, lbl, parent):
        SubModule.__init__(self, lbl, parent)
        self._title = xfg.ODKH2Title("", self._label, "left", "#ed8a78", self._hint, self._media)

    def export(self, df, questions):
        row = pd.DataFrame([["begin_repeat","REP{}".format(self._reference),self._title.getLabel(),"","","table-list","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        for q in self._question_list:
            df = questions.get()[q].export(df)
        row = pd.DataFrame([["end_repeat","","","","","","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        return df

class DiagnosisAgreementSubModule(SubModule):

    def __init__(self, lbl, parent):
        SubModule.__init__(self, lbl, parent)
        self._title = xfg.ODKH2Title("", self._label, "left", "#ed8a78", self._hint, self._media)

    def export(self, df, diagnoses):
        row = pd.DataFrame([["begin_group","TAB{}".format(self._reference),self._title.getLabel(),"","","table-list","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        for q in self._question_list:
            agreement = diagnoses.get()[q].getDiagnosisAgreement()
            if agreement is not None:
                df = agreement.getODKQuestion().export(df)
        row = pd.DataFrame([["end_group","","","","","","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        return df

class ManagementAgreementSubModule(SubModule):

    def __init__(self, lbl, parent):
        SubModule.__init__(self, lbl, parent)
        self._title = xfg.ODKH2Title("", self._label, "left", "#ed8a78", self._hint, self._media)

    def export(self, df, managements):
        row = pd.DataFrame([["begin_group","TAB{}".format(self._reference),self._title.getLabel(),"","","table-list","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        for q in self._question_list:
            agreement = managements.get()[q].getManagementAgreement()
            if agreement is not None:
                df = agreement.getODKQuestion().export(df)
        row = pd.DataFrame([["end_group","","","","","","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        return df

class TreatmentAgreementSubModule(SubModule):

    def __init__(self, lbl, parent):
        SubModule.__init__(self, lbl, parent)
        self._title = xfg.ODKH2Title("", self._label, "left", "#ed8a78", self._hint, self._media)

    def export(self, df, treatments):
        row = pd.DataFrame([["begin_group","TAB{}".format(self._reference),self._title.getLabel(),"","","table-list","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        for q in self._question_list:
            agreement = treatments.get()[q].getAgreement()
            if agreement is not None:
                df = agreement.getODKQuestion().export(df)
        row = pd.DataFrame([["end_group","","","","","","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        return df

class RegistrationModule(Module):

    def __init__(self, lbl, asws):
        Module.__init__(self, lbl)

        # Displayed questions
        registration_questions = [
            "First name",
            "Last name",
            "Sex",
            "Does the child have a study ID?",
            "Please scan the child's study ID",
            "If QR code scanning is not possible, please manually enter the child's study ID",
            "Exact date of birth known?",
            "Date of birth",
            "Year and month of birth known?",
            "Year and month of birth",
            "Age category",
            "Age in months",
            "Age in days"
        ]
        for q in registration_questions:
            self.addQuestion(q)

class ConsultationModule(Module):
    
    def __init__(self, lbl, header):
        '''
        if "weight" in header.keys():
            h += " - Weight: ${{{0}}}kg".format(header['weight'])
        '''
        Module.__init__(self, lbl, header)

class CalculationModule(Module):
    
    def __init__(self, lbl):
        Module.__init__(self, lbl)

    def export(self, df, key, questions, diagnoses, managements, treatments):
        for q in self._question_list:
            df = questions.get()[q].export(df)
        return df

class DiagnosisCalculationModule(Module):
    
    def __init__(self, lbl):
        Module.__init__(self, lbl)

    def export(self, df, key, questions, diagnoses, managements, treatments):
        for q in self._question_list:
            if key in diagnoses.get()[q].getCalculations():
                calc = diagnoses.get()[q].getCalculations()[key]
                if calc is not None:
                    if type(calc) is cobj.Boolean:
                        df = calc.getODKQuestion().export(df)
                    else:
                        df = calc.export(df)
        row = pd.DataFrame([["","","","","","","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        return df

class ManagementCalculationModule(Module):
    
    def __init__(self, lbl):
        Module.__init__(self, lbl)

    def export(self, df, key, questions, diagnoses, managements, treatments):
        for q in self._question_list:
            cdict = managements.get()[q].getCalculations()
            for calc in cdict.values():
                if calc is not None:
                    if type(calc) is cobj.Boolean:
                        df = calc.getODKQuestion().export(df)
                    else:
                        df = calc.export(df)
        row = pd.DataFrame([["","","","","","","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        return df

class TreatmentCalculationModule(Module):

    def __init__(self, lbl):
        Module.__init__(self, lbl)

    def export(self, df, key, questions, diagnoses, managements, treatments):
        for q in self._question_list:
            cdict = treatments.get()[q].getCalculations()
            for calc in cdict.values():
                if calc is not None:
                    if type(calc) is cobj.Boolean:
                        df = calc.getODKQuestion().export(df)
                    else:
                        df = calc.export(df)
        row = pd.DataFrame([["","","","","","","","","","","","","","","","","","","","","","","",""]], columns=df.columns.values)
        df = df.append(row)
        return df

class ObjectDict:
    
    def __init__(self):
        self._dict = dict()

    def add(self, obj):
        self._dict[obj.getLabel()] = obj

    def getItem(self, lbl):
        return self._dict[lbl]

    def get(self):
        return self._dict

    def print(self):
        print(self._dict)

class QuestionDict(ObjectDict):
    
    def __init__(self):
        ObjectDict.__init__(self)

    def addQuestions(self, arg, answers):
        for val in arg:
            if val['type'] == "demographics":
                if val['odk_type'] == "time duration":
                    d = cobj.Demographics(val)
                    d.addODKInteger()
                elif val['odk_type'] == "select_one":
                    val["answers"] = answers.getItem(val["asw_lbl"])
                    d = cobj.Demographics(val)
                    d.addODKSelectOne()
                elif val['odk_type'] == "date":
                    d = cobj.Demographics(val)
                    d.addODKDate()
            elif val['type'] == "observed sign":
                val["answers"] = answers.getItem(val["asw_lbl"])
                d = cobj.ObservedSign(val)
                d.addODKSelectOne()
            elif val['type'] == "symptom":
                val["answers"] = answers.getItem(val["asw_lbl"])
                d = cobj.Symptom(val)
                d.addODKSelectOne()
            elif val['type'] == "time duration":
                d = cobj.TimeDuration(val)
                d.addODKInteger()
            elif val['type'] == "quantity":
                d = cobj.Quantity(val)
                d.addODKInteger()
            elif val['type'] == "measurement":
                if val['odk_type'] == "integer":
                    d = cobj.Measurement(val)
                    d.addODKInteger()
                if val['odk_type'] == "range":
                    d = cobj.Measurement(val)
                    d.addODKRange()
            elif val['type'] == "boolean":
                d = cobj.Boolean(val)
                d.addODKCalculation()
            elif val['type'] == "calculation":
                d = cobj.Calculation(val)
                d.addODKCalculation()
            elif val['type'] == "pii":
                if val['odk_type'] == "free_text":
                    d = cobj.PII(val)
                    d.addODKText()
            elif val['type'] == "research":
                if val['odk_type'] == "barcode":
                    d = cobj.Research(val)
                    d.addODKBarcode()
                elif val['odk_type'] == "select_one":
                    val["answers"] = answers.getItem(val["asw_lbl"])
                    d = cobj.Research(val)
                    d.addODKSelectOne()
                elif val['odk_type'] == "free_text":
                    d = cobj.Research(val)
                    d.addODKText()
            self._dict[val['label']] = d.getODKQuestion()

class AnswerDict(ObjectDict):
    
    def __init__(self):
        ObjectDict.__init__(self)
        d = {
            "AGREEMENT":[
                "Disagree",
                "Agree"],
            "POSSIBLE":[
                "Not possible",
                "Possible"],
            "AVAILABLE":[
                "Not available",
                "Available"],
            "YESNO":[
                "No",
                "Yes"],
            "YESNO_NA":[
                "No",
                "Yes",
                "N/A"],
            "SEX":[
                "Male",
                "Female",
                "Other"],
            "MCAT":[
                "2 months and less",
                "2-59 months"],
            "BIRTHDATE":[
                "Exact birthdate known (day - month - year)",
                "Only month and year known",
                "Only birthyear known"]}
        self.addAnswers(d)

    def add(self, asw):
        self._dict[asw.getRef()] = asw

    def addAnswers(self, arg):
        for key, val in arg.items():
            self.add(xfg.ODKAnswer(key, val))

    def ODKExport(self, choices_df):
        for val in self._dict.values():
            choices_df = val.export(choices_df)
        return choices_df

class DiagnosisDict(ObjectDict):
    
    def __init__(self):
        ObjectDict.__init__(self)

    def addDiagnoses(self, arg, severity, asws):
        for val in arg:
            self.add(cobj.Diagnosis(val, severity, asws))

class ManagementDict(ObjectDict):
    
    def __init__(self):
        ObjectDict.__init__(self)

    def addManagements(self, arg, asws):
        for val in arg:
            self.add(cobj.Management(val, asws))

class TreatmentDict(ObjectDict):
    
    def __init__(self):
        ObjectDict.__init__(self)

    def addTreatments(self, arg, asws):
        for val in arg:
            self.add(cobj.Treatment(val, asws))