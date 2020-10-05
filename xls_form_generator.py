import pandas as pd
import os
import my_utils
import calculations as calc

def initialiseXLSForm(form_title, form_id, version, languages, def_language):

    # Survey sheet
    survey_col_names = ["type", "name"]
    for lg in languages:
        survey_col_names.append("label::"+lg)
    survey_col_names += ["appearance", "relevant", "constraint", "calculation", "required", "default"]
    for lg in languages:
        survey_col_names.append("hint::"+lg)
        survey_col_names.append("constraint_message::"+lg)
        survey_col_names.append("required_message::"+lg)
        survey_col_names.append("media::image::"+lg)
    survey_col_names += ["parameters"]
    survey_df = pd.DataFrame(columns = survey_col_names)

    # Choices sheet
    choices_col_names = ["list_name", "name"]
    for lg in languages:
        choices_col_names.append("label::"+lg)
        choices_col_names.append("media::image::"+lg)
    choices_df = pd.DataFrame(columns = choices_col_names)

    # Settings sheet
    settings_col_names = ["form_title", "form_id", "instance_name", "version", "style", "default_language"]
    settings_df = pd.DataFrame(columns = settings_col_names)
    settings_df.loc[0] = [form_title, form_id, "concat('timci-crf-day7-', uuid())", version, "pages", def_language]

    return survey_df, choices_df, settings_df

def writeXLSForm(path, survey_df, choices_df, settings_df):

    if os.path.exists(path):
        os.remove(path)
    writer = pd.ExcelWriter(path, engine = 'xlsxwriter')
    survey_df.to_excel(writer, sheet_name = 'survey', index=False)
    choices_df.to_excel(writer, sheet_name = 'choices', index=False)
    settings_df.to_excel(writer, sheet_name = 'settings', index=False)
    writer.save()
    writer.close()

#################
# ODK Questions #
#################

class ODKQuestion:
    
    def __init__(self, arg):
        self._row  = dict()
        self._keys = [
            'reference',
            'type', 
            'label',
            'appearance',
            'cond',
            'calculation',
            'required',
            'required_msg',
            'constr',
            'constr_msg',
            'media',
            'default',
            'hint',
            'parameters']
        for k in self._keys:
            if k in arg.keys():
                self._row[k] = arg[k]
            else:
                self._row[k] = ""
        self._complex_conditions = None
        
    def addTopConditionQuestion(self, q, asw, logic="or", group=0):
        cond = calc.EqualAnswerCond(q, asw)
        if self._complex_conditions is None:
            self._complex_conditions = calc.ComplexConditions([{'cond':cond.get(),'logic':logic, 'group':group}])
        else:
            self._complex_conditions.addCondition([{'cond':cond.get(),'logic':logic, 'group':group}])
        self._row['cond'] = self._complex_conditions.getConditionStr()

    def addTopConditionCalculation(self, q, asw, logic="or", group=0):
        cond = calc.EqualCalculationCond(q, asw)
        if self._complex_conditions is None:
            self._complex_conditions = calc.ComplexConditions([{'cond':cond.get(),'logic':logic, 'group':group}])
        else:
            self._complex_conditions.addCondition([{'cond':cond.get(),'logic':logic, 'group':group}])
        self._row['cond'] = self._complex_conditions.getConditionStr()
    
    def getTopCondition(self):
        return self._row['cond']
    
    def getRef(self):
        return self._row['reference']

    def getLabel(self):
        return self._row['label']

    def getCalculation(self):
        return self._row['calculation']
    
    def export(self, df):
        vec = [self._row['type'],
               self._row['reference'],
               self._row['label'],
               "",
               "",
               self._row['appearance'],
               self._row['cond'],
               self._row['constr'],
               self._row['calculation'],
               self._row['required'],
               self._row['default'],
               self._row['hint'],
               self._row['constr_msg'],
               self._row['required_msg'],
               self._row['media'],
               "",
               "",
               "",
               self._row['media'],
               "",
               "",
               "",
               self._row['media'],
               self._row['parameters']]
        row = pd.DataFrame([vec], columns=df.columns.values)
        df = df.append(row)
        return df
    
    def print(self):
        print(self._row['reference'], self._row['label'])

class ODKWelcomeScreen(ODKQuestion):
    def __init__(self, ref, titles, media):
        lbl = ""
        for title in titles:
            new_lbl = my_utils.formatTitle(title['label'], title['level'], "center", title['color'])
            if not lbl:
                lbl = new_lbl
            else:
                lbl += new_lbl
        ODKQuestion.__init__(self, {'type':'note','reference:':ref, 'label': lbl, 'media':media})

# ODK title notes
class ODKTitle(ODKQuestion):
    def __init__(self, ref, lbl, lvl, align, color, hint, media):
        ODKQuestion.__init__(self, {'type':'note','reference:':ref, 'label':my_utils.formatTitle(lbl, lvl, align, color), 'hint':hint, 'media':media})

class ODKH1Title(ODKTitle):
    def __init__(self, ref, lbl, align, color, hint, media):
        ODKTitle.__init__(self, ref, lbl, 1, align, color, hint, media)

class ODKH2Title(ODKTitle):
    def __init__(self, ref, lbl, align, color, hint, media):
        ODKTitle.__init__(self, ref, lbl, 2, align, color, hint, media)

class ODKSelectOne(ODKQuestion):
    
    def __init__(self, arg):
        ODKQuestion.__init__(self, arg)
        self._row['answers'] = arg['answers']
        self._row['type'] = "select_one {}".format(self._row['answers'].getRef())
        
    def getAnswer(self, lbl):
        return self._row['answers'].getAnswer(lbl)
        
class ODKAnswer:
    
    def __init__(self, ref, asw_list):
        self._row = dict()
        self._row['reference'] = ref
        self._answers = dict()
        for i in range(len(asw_list)):
            self._answers[i] = asw_list[i]
        
    def getRef(self):
        return self._row['reference']
    
    def getAnswer(self, lbl):
        for k, asw in self._answers.items():
            if asw == lbl:
                return k

    def getAnswers(self):
        asws = []
        for k, asw in self._answers.items():
            asws.append(asw)
        return asws
        
    def export(self, df):
        for k, asw in self._answers.items():
            val = [self._row['reference'], k, asw, "", "", "", "", ""]
            row = pd.DataFrame([val], columns=df.columns.values)
            df = df.append(row)
        row = pd.DataFrame([["", "", "", "", "", "", "", ""]], columns=df.columns.values)
        df = df.append(row)
        return df