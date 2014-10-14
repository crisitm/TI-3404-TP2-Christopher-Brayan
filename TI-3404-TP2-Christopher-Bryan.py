
import sys, copy, re #librerias 
rules     = [] #reglas
trace     = 0 #seguimiento
goalId    = 100 #identificador meta

def fatal (mesg) : #manejo de errores
    sys.stdout.write ("Fail: %s\n" % mesg)
    sys.exit(1) #salida del programa

class Term :
    def __init__ (self, s) :   # se espera algo como "x(y,z...)"
        if s[-1] != ')' : fatal("error de sintaxis con la clausula: %s" % [s]) #manejo de errores
        flds = s.split('(')
        if len(flds) != 2 : fatal("error de sintaxis con la clausula: %s" % [s]) #manejo de errores
        self.args = flds[1][:-1].split(',') 
        self.pred = flds[0]

    def __repr__ (self) :
        return "%s(%s)" % (self.pred,",".join(self.args))

class Rule :
    def __init__ (self, s) :   # se espera "term-:term;term;..."
        flds = s.split(":-")
        self.head = Term(flds[0])
        self.goals = []
        if len(flds) == 2 :
            flds = re.sub("\),",");",flds[1]).split(";") #manejo de errores
            for fld in flds : self.goals.append(Term(fld))

    def __repr__ (self) :
        rep = str(self.head)  #se toma la estructura a evaluar
        sep = " :- "
        for goal in self.goals : #se el antes y despues de la definicion.
            rep += sep + str(goal)
            sep = ","
        return rep
        
class Goal :
    def __init__ (self, rule, parent=None, env={}) : #se evalua la meta
        global goalId  #se evalua la meta segun corresponda 
        self.id = goalId
        self.rule = rule
        self.parent = parent
        self.env = copy.deepcopy(env)
        self.inx = 0       # Iniciar la búsqueda con primer subgoal

    def __repr__ (self) :
        return "Goal %d rule=%s inx=%d env=%s" % (self.id,self.rule,self.inx,self.env)

def main () :
    for file in sys.argv[1:] :
        if file == '.' : return    # termina la clausula
        procFile(open(file),'')    # archivo en la línea de comandos
    procFile (sys.stdin,'? ')      # permite al usuario ingresar el hecho o la regla

def procFile (f, prompt) :
    global rules, trace  #estructura para procesar los datos entrantes 
    env = []
    while 1 :
        if prompt :
            sys.stdout.write(prompt)
            sys.stdout.flush()
        sent = f.readline()
        if sent == "" : break
        s = re.sub("#.*","",sent[:-1])   # comentarios y de nueva línea
        s = re.sub(" ", "",s)           # eliminar espacios
        if s == "" : continue

        if s[-1] in '?.' : punc=s[-1]; s=s[:-1]
        else             : punc='.'

        if   s == 'trace=0' : trace = 0
        elif s == 'trace=1' : trace = 1
        elif s == 'quit'    : sys.exit(0)
        elif s == 'dump'  :
            for rule in rules : print (rule)
        elif punc == '?' : search(Term(s)) # se hace la busqueda del Term
        else             : rules.append(Rule(s))

# Una meta es una regla en en un cierto punto.
# Env contiene definiciones de indices del term actual
# satisfacer , "padres" son aqueyos "goal" que dieron origen al nuevo goal y que
# se toma en cuenta el backtracking
#

def unify (srcTerm, srcEnv, destTerm, destEnv) : # funcion que valida la unificacion 
    "actualiza y retorna true si unifica correctamente"
    nargs = len(srcTerm.args)
    if nargs        != len(destTerm.args) : return 0
    if srcTerm.pred != destTerm.pred      : return 0
    for i in range(nargs) :
        srcArg  = srcTerm.args[i]
        destArg = destTerm.args[i]
        if srcArg <= 'Z' : srcVal = srcEnv.get(srcArg)
        else             : srcVal = srcArg
        if srcVal :    # constante o variable definida en el codigo
            if destArg <= 'Z' :  # variable destino
                destVal = destEnv.get(destArg)
                if not destVal : destEnv[destArg] = srcVal  # unifica !
                elif destVal != srcVal : return 0           # No unifica
            elif     destArg != srcVal : return 0           # No unifica
    return 1

def search (term) :
    global goalId
    goalId = 0
    if trace : print ("search", term)
    goal = Goal(Rule("got(goal):-x(y)"))      # acaba de obtener un objeto de regla
    goal.rule.goals = [term]                  # target, es un simple goal
    if trace : print ("stack", goal)
    stack = [goal]                            # Iniciar la búsqueda
    while stack :
        c = stack.pop()        # proximo goal a evaluar
        if trace : print ("  pop", c)
        if c.inx >= len(c.rule.goals) :       # ya termino el goal actual?
            if c.parent == None :             #yes. es el goal original?
                if c.env : print (c.env)       # Yes. avisar al usuario que se encontro una solucion
                else     : print ("Yes")        
                continue
            parent = copy.deepcopy(c.parent)  # de lo contrario reanudar el goal padre
            unify (c.rule.head,                  c.env,
                   parent.rule.goals[parent.inx],parent.env)
            parent.inx = parent.inx+1         # avanzar al siguiente goal en el cuerpo de las metas
            if trace : print ("stack", parent)
            stack.append(parent)              # esperar su turno
            continue

        # No. en este caso nada mas que hacer con este goal.
        term = c.rule.goals[c.inx]            # lo que se quiere resolver
        for rule in rules :                     # seguir bajando en la base de datos de reglas
            if rule.head.pred      != term.pred      : continue
            if len(rule.head.args) != len(term.args) : continue
            child = Goal(rule, c)               # un posible subgoal
            ans = unify (term, c.env, rule.head, child.env)
            if ans :                            # si unifica, sube en la cola
                if trace : print ("stack", child)
                stack.append(child)
            #else : print ("No")    

if __name__ == "__main__" : main ()













