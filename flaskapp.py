from flask import Flask,render_template,request,flash
from math import radians, cos, sin, asin, sqrt
import sys
import MySQLdb
import math
import redis


app = Flask(__name__)

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    
    
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
   
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r
#@app.route('/',methods=['POST','GET'])
@app.route('/pkbjhb')
def test():
    #AWS Credentials
    db = MySQLdb.connect("AWS RDB connection link.","username","password","DB Instance Name.")
    print("1")
    cursor = db.cursor()
    print("2")
    r_server = redis.Redis("Redis domain.")
    print("3")
    cursor.execute("SELECT City,Latitude,Longitude FROM cities")
    print("4")
    rows=cursor.fetchall()
    print("5")
    for row in rows:
        print(row[0]+ str(row[1])+";"+str(row[2]))
        r_server.set(row[0], str(row[1])+";"+str(row[2]))
        
    db.close()
    return render_template('city.html')
    
@app.route('/',methods=['POST','GET'])
def func1():
    return render_template('city.html')

@app.route('/nearestpage',methods=['POST','GET'])
def func2():
    return render_template('nearest.html')

@app.route('/bydistpage',methods=['POST','GET'])
def func3():
    return render_template('bydist.html')
    
@app.route('/nearestcompute',methods=['POST','GET'])
def hello_world():
    if request.method == 'POST':
        db = MySQLdb.connect("AWS RDB connection link.","username","password","DB Instance Name.")
        cursor = db.cursor()
        city=request.form['city']
        #dist=request.form['distanceradius']
        #dist=float(dist)
        dist=20 
        
        limit=request.form['limit']
        limit= int(limit)
        r_server = redis.Redis("Redis domain.")
        
        abc = r_server.smembers(city+"_nearest_limit_"+str(limit))
        if len(abc) != 0 :
                return """
                <!doctype html>
                <title>Nearest Cities</title>
                <h1>Nearest Cities</h1>
                %s"""%str(list(abc))
        dist=dist/1.6;
        
        
        cursor.execute("SELECT Latitude,Longitude FROM cities WHERE City LIKE %s",[city])
        rows=cursor.fetchall()
        for row in rows:
             mylat=float(row[0])
             mylon=float(row[1])
        print("city = "+city+"latitude = "+str(mylat)+"longitude = "+str(mylon))
         
        incr_bound_box = True
        while incr_bound_box :
            div=abs(math.cos(math.radians(mylat))*69)
            #print(div)
            lon1 = mylon-dist/div
             
             
             
            lon2 = mylon+dist/abs(math.cos(math.radians(mylat))*69)
            lat1 = mylat-(dist/69)
            lat2 = mylat+(dist/69)
            #print("long1 = "+str(lon1))
            #print("long2 = "+str(lon2))
            #print("lat1 = "+str(lat1))
            #print("lat2 = "+str(lat2))
            cursor.execute("SELECT dest.City,dest.Latitude,dest.Longitude as city from cities dest where dest.Longitude between %s and %s and dest.Latitude between %s and %s",[str(lon1),str(lon2),str(lat1),str(lat2)])
            r=cursor.fetchall()
            content=[]
            for row in r:
                dict ={"city":row[0],"latitude":row[1],"longitude":row[2],"distance_difference":haversine(float(row[2]),float(row[1]),float(mylon),float(mylat))}
                content.append(dict)
                #print(str(dict))
                
            sorted_content = sorted(content, key=lambda k: k['distance_difference']) 
            if (len(sorted_content) > limit) :
                incr_bound_box =False
            else :
                dist = 2 * dist
                print("bounding box doubled. dist = "+str(dist))
        i=0
        str_cities=""
        r_server.delete(city+"_nearest_limit_"+str(limit))
        for ele in sorted_content:
            #print(str(ele))
            r_server.sadd(city+"_nearest_limit_"+str(limit), ele['city'])
            str_cities = str_cities+ele['city']+";"
            i=i+1
            if i==limit :
                
                print(str_cities)
                break
                
                  
            
        db.close()
        return """
                <!doctype html>
                <title>Nearest Cities</title>
                <h1>Nearest Cities</h1>
                %s"""%str_cities

    
@app.route('/bydistcompute',methods=['POST','GET'])
def hello_world_dist():
    if request.method == 'POST':
        db = MySQLdb.connect("AWS RDB connection link.","username","password","DB Instance Name.")
        cursor = db.cursor()
        city=request.form['city']
        dist=request.form['distanceradius']
        dist=float(dist)
        #limit=request.form['limit']
        limit = 100
        r_server = redis.Redis("Redis domain.")
        entereddist=dist
        abc = r_server.smembers(city+"_dist_"+str(entereddist))
        if len(abc) != 0 :
                return """
                <!doctype html>
                <title>Nearest Cities</title>
                <h1>Nearest Cities</h1>
                %s"""%str(list(abc))
        
        dist=dist/1.6;
        
        
        cursor.execute("SELECT Latitude,Longitude FROM cities WHERE City LIKE %s",[city])
        rows=cursor.fetchall()
        for row in rows:
             mylat=float(row[0])
             mylon=float(row[1])
        print("city = "+city+" latitude = "+str(mylat)+"longitude = "+str(mylon))
         
        
        div=abs(math.cos(math.radians(mylat))*69)
        #print(div)
        lon1 = mylon-dist/div
         
         
         
        lon2 = mylon+dist/abs(math.cos(math.radians(mylat))*69)
        lat1 = mylat-(dist/69)
        lat2 = mylat+(dist/69)
        #print("long1 = "+str(lon1))
        #print("long2 = "+str(lon2))
        #print("lat1 = "+str(lat1))
        #print("lat2 = "+str(lat2))
        cursor.execute("SELECT dest.City,dest.Latitude,dest.Longitude as city from cities dest where dest.Longitude between %s and %s and dest.Latitude between %s and %s",[str(lon1),str(lon2),str(lat1),str(lat2)])
        r=cursor.fetchall()
        content=[]
        for row in r:
            dict ={"city":row[0],"latitude":row[1],"longitude":row[2],"distance_difference":haversine(float(row[2]),float(row[1]),float(mylon),float(mylat))}
            content.append(dict)
            #print(str(dict))
            
        sorted_content = sorted(content, key=lambda k: k['distance_difference']) 
        
        i=0
        str_cities=""
        r_server.delete(city+"_dist_"+str(dist))
        for ele in sorted_content:
            #print(str(ele))
            r_server.sadd(city+"_dist_"+str(entereddist), ele['city'])
            str_cities = str_cities+ele['city']+";"
            i=i+1
        
        
        
                
                  
            
        db.close()
        
        return """
                <!doctype html>
                <title>Nearest Cities</title>
                <h1>Nearest Cities</h1>
                %s"""%str_cities
   


if __name__ == '__main__':
    app.secret_key='Hello world'
    app.debug = True
    app.run()
