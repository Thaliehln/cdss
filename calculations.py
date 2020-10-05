class BooleanCalculation():

    def __init__(self, conditions, istrue, isfalse):
        self._cond = ComplexConditions(conditions)
        self._istrue = istrue
        self._isfalse = isfalse
        self._formula = "if({0}, {1}, {2})".format(self._cond.getConditionStr(), self._istrue, self._isfalse)

    def getComplexConditions(self):
        return self._cond

    def getFormula(self):
        return self._formula

    def addCondition(self, condition_list):
        self._cond.addCondition(condition_list)
        self._formula = "if({0}, {1}, {2})".format(self._cond.getConditionStr(), self._istrue, self._isfalse)

#############
# Condition #
#############

class Condition():

    def __init__(self, cond):
        self._cond = cond

    def get(self):
        return self._cond

class EqualAnswerCond(Condition):
    
    def __init__(self, q, asw):
        Condition.__init__(self, "${{{0}}}={1}".format(q.getRef(), q.getAnswer(asw)))

class EqualCalculationCond(Condition):
    
    def __init__(self, q, asw):
        Condition.__init__(self, "${{{0}}}={1}".format(q.getRef(), asw))

class NotEqualAnswerCond(Condition):
    
    def __init__(self, q, asw):
        Condition.__init__(self, "${{{0}}}!={1}".format(q.getRef(), q.getAnswer(asw)))

class SupEqual2ThresCond(Condition):
    
    def __init__(self, q, thres):
        Condition.__init__(self, "${{{0}}}>={1}".format(q.getRef(), thres))

class Sup2ThresCond(Condition):
    
    def __init__(self, q, thres):
        Condition.__init__(self, "${{{0}}}>{1}".format(q.getRef(), thres))

class InfEqual2ThresCond(Condition):
    
    def __init__(self, q, thres):
        Condition.__init__(self, cond = "${{{0}}}<={1}".format(q.getRef(), thres))
    
class Inf2ThresCond(Condition):
    
    def __init__(self, q, thres):
        Condition.__init__(self, cond = "${{{0}}}<{1}".format(q.getRef(), thres))

class CombinedConditions():

    def __init__(self, condition_list):
        self._cond = ""
        self._condition_list = []
        self.addCondition(condition_list)

    def addCondition(self, condition_list):
        for v in condition_list:
            new_cond = v['cond']
            logic = v['logic']
            if self._cond == "":
                self._cond = new_cond
            else:
                if v['sep']:
                    self._cond = "({0}) {1} ({2})".format(self._cond, logic, new_cond)
                else:
                    self._cond = "{0} {1} {2}".format(self._cond, logic, new_cond)
        self._condition_list += condition_list

    def getCondition(self):
        return self._cond

    def getConditionList(self):
        return self._condition_list

class ComplexConditions():

    def __init__(self, arg):
        self._condition_dict = dict()
        self._condition_dict[0] = {"cond_string": arg[0]['cond'], "condition_list":[{"cond": arg[0]['cond']}]}
        if len(arg)>1:
            self.addCondition(arg[1:])

    def addCondition(self, conditions):
        for item in conditions:
            if item['group'] in self._condition_dict.keys():
                self._condition_dict[item['group']]["cond_string"] = "{0} {1} {2}".format(self._condition_dict[item['group']]["cond_string"], item['logic'], item['cond'])
                self._condition_dict[item['group']]["condition_list"].append(item)            
            else:
                self._condition_dict[item['group']] = {"cond_string": item['cond'], "condition_list":[{"cond": item['cond']}], "logic":item['logic']}

    def getConditionStr(self):
        s = ""
        for val in self._condition_dict.values():
            if "logic" in val.keys():
                s += " {} ({})".format(val["logic"], val["cond_string"])
            else:
                s += "({})".format(val["cond_string"])
        return s

    def getConditionDict(self):
        return self._condition_dict

if __name__ == "__main__":
    
    cond = [{'cond':"A >= 30"}]
    cc = ComplexConditions(cond)
    print(cc.getConditionStr())

    b = BooleanCalculation(cond, 1, 0)
    print(b.getComplexConditions().getConditionStr())

    cond2 = [{"cond": "B < 3", "logic":"or", "group":0}, {"cond": "G <= 25", "logic":"and", "group":1}]
    cc.addCondition(cond2)
    print(cc.getConditionStr())
    cond3 = [{"cond": "C == 50", "logic":"and", "group":1}]
    cc.addCondition(cond3)
    print(cc.getConditionStr())
    cond3 = [{"cond": "D > 70", "logic":"and", "group":1}]
    cc.addCondition(cond3)
    print(cc.getConditionStr())
    cond4 = [{"cond": "E > 70", "logic":"and", "group":0}]
    cc.addCondition(cond4)
    print(cc.getConditionStr())
    print(cc.getConditionDict())

    cond = [{'cond':cc.getConditionStr()}]
    cc = ComplexConditions(cond)
    print(cc.getConditionStr())
    cond2 = [{"cond": "Z < 3", "logic":"or", "group":1}]
    cc.addCondition(cond2)
    print(cc.getConditionStr())