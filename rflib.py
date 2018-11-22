import math
class rflib:
    def db2uv(db):
        pp1 = (10.0 ** (db/10.0)) * 50.0 * (10**-3)
        pp2 = math.sqrt(pp1)
        uv = pp2 * (10**6)
        return(uv)
    def uv2db(uv):
        pp1 = 20.0 * math.log10(uv)
        pp2 = 10.0 * math.log10(50.0)
        db = pp1 - pp2 - 90.0
        return(db)
    def db2w(db):
        Kw = 10**(db/10.0)
        w = Kw/1000.0
        return(w)
    def w2db(w):
        db = 10.0 * math.log10(1000.0 * w)
        return(db)
    def rl2swr(rl):
        pp1 = 10.0 ** (rl/20.0)
        swr = (pp1+1.0) / (pp1-1.0)
        return(swr)
    """ the AD8318 has an output of 1.8v @-55db
        0.6v at -5 db
        slope -24 mv/db?
        usefull from -60db to 0db.
    """
    def ad2db(mv):
        v1 = mv -1000.0
        p1 = v1 / -23.0
        db = p1 -19
        return(db)

    if __name__ == '__main__':
        uv5 = db2uv(5)
        print("5db = %f uv" % uv5)
        uv4 = db2uv(-4)
        print("-4db = %f uv expecting 141086" % uv4)
        uv0 = db2uv(0)
        print("0db = %f uv expecting 226307" % uv0)
        uv0 = db2uv(-125)
        print("-125db = %f uv expecting 0.13" % uv0)
        db = uv2db(0.13)
        print("0.13uv = %f db expecting -124.7" % db)
        w=db2w(43)
        print("43 dbm = %f expecting 19.9526" %w)
        w=db2w(-30)
        print("-30 dbm = %f expecting 0.000001" %w)
        w=db2w(0)
        print("0 dbm = %f expecting 0.001" %w)
        w=db2w(30)
        print("30 dbm = %f expecting 1" %w)
        w = w2db(1)
        print("1w = %f expecting 30" % w)
        w = w2db(20)
        print("20w = %f expecting 43" % w)
        swr = rl2swr(1)
        print("rl 1 = %f swr expecting 17.4" %swr)
        swr = rl2swr(40)
        print("rl 40 = %f swr expecting 1.02" %swr)
        db = ad2db(2.0 * 1000.0)
        print("2.0v = %f db (-65)" % db)    
        db = ad2db(0.6*1000.0)
        print("0.6v = %f db (-5)" % db)    
        db = ad2db(1.0*1000.0)
        print("1v = %f db (-19)" % db)    
        db = ad2db(0.78*1000.0)
        print("0.78v = %f db (-10)" % db)    
        db = ad2db(1.52*1000.0)
        print("1.52v = %f db (-40)" % db)    
