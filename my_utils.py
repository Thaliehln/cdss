import hashlib

def strHash(s):
    n = int(hashlib.sha1(s).hexdigest(), 16) % (10 ** 5)
    ns = "{0:05d}".format(n)
    return ns

def formatConstraint(constr):
    text = ".>= {} and .<= {}".format(constr[0], constr[1])
    return text

def formatConstraintMsg(constr):
    text = "Entry must be superior or equal to {} and inferior or equal to {}".format(constr[0], constr[1])
    return text

def formatTitle(lbl, lvl, align, color):
    return '<h{0} style="text-align: {1};"><span style="color:{2}">{3}</span></h{0}>'.format(lvl, align, color, lbl.upper())