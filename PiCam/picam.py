import serial
import time
import atexit
from functools import wraps
from flask import Flask, render_template, request, Response
app = Flask(__name__)

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'secret'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# This function maps the angle we want to move the servo to, to the needed PWM value
def angleMap(angle):
	value = int((round((2000.0/180.0),0)*angle) -1000)
	if(value > 1000):
		return 1000
	elif(value < -1000):
		return -1000
	else:
		return value;

# Create a dictionary called pins to store the pin number, name, and angle
pins = {
    23 : {'name' : 'pan', 'angle' : 90},
    22 : {'name' : 'tilt', 'angle' : 90}
    }

#defines the speed of the movement
speed = 5

#define inverse
paninverse = 1
tiltinverse = -1

def cleanup():
	print("Exit app")

def sendPosition(motor, position):
	#Initialise the serial interface
	s=serial.Serial("/dev/ttyAMA0",9600)
	if(s.isOpen()):
     		s.close()
	s.open()
	if motor == "pan":
		s.write("s0 "+str(position)+" 5\n")
	elif motor == "tilt":
     		s.write("s1 "+str(position)+" 5\n")
	s.close()
	return "Moved"

def sendBothPosition(positionPan, positionTilt):
        #Initialise the serial interface
        s=serial.Serial("/dev/ttyAMA0",9600)
        if(s.isOpen()):
                s.close()
        s.open()
        s.write("s0 "+str(positionPan)+" 5\n")
        s.write("s1 "+str(positionTilt)+" 5\n")
        s.close()
        return "Moved"


# Load the main form template on webrequest for the root page
@app.route("/")
@requires_auth
def main():

    # Create a template data dictionary to send any data to the template
    templateData = {
        'title' : 'PiCam'
        }
    # Pass the template data into the template picam.html and return it to the user
    return render_template('picam.html', **templateData)

# The function below is executed when someone requests a URL with a move direction
@app.route("/<direction>")
def move(direction):
    global speed
    global titlinverse
    global paninverse
    # Choose the direction of the request
    if direction == 'left':
	    # Increment the angle by speed
        na = pins[23]['angle'] + paninverse * speed
        # Verify that the new angle is not too great
        if int(na) <= 180:
            # Change the angle of the servo
            sendPosition(pins[23]['name'],angleMap(na))
	    print("Servo 23 at %s" % (angleMap(na)))
            # Store the new angle in the pins dictionary
            pins[23]['angle'] = na
	else:
	    pins[23]['angle'] = 180
        return str(na) + ' ' + str(angleMap(na))
    elif direction == 'reset':
	sendBothPosition(0,0)
	pins[23]['angle'] = 90
	pins[22]['angle'] = 90
	return '0 0'	
    elif direction == 'right':
        na = pins[23]['angle'] - paninverse *speed
        if na >= 0:
	    sendPosition(pins[23]['name'],angleMap(na))
	    print("Servo 23 at %s" % (angleMap(na)))
            pins[23]['angle'] = na
	else :
	    pins[23]['angle'] = 0
        return str(na) + ' ' + str(angleMap(na))
    elif direction == 'up':
        na = pins[22]['angle'] + tiltinverse * speed
        if na <= 180:
            sendPosition(pins[22]['name'],angleMap(na))
	    print("Servo 22 at %s" % (angleMap(na)))
            pins[22]['angle'] = na
	else :
	    pins[22]['angle'] = 180
        return str(na) + ' ' + str(angleMap(na))
    elif direction == 'down':
        na = pins[22]['angle'] - tiltinverse * speed
        if na >= 0:
            sendPosition(pins[22]['name'],angleMap(na))
            print("Servo 22 at %s" % (angleMap(na)))
            pins[22]['angle'] = na
	else :
	    pins[22]['angle'] = 0
        return str(na) + ' ' + str(angleMap(na))
    elif direction == 'speed1':
	speed = 1
	return str(speed)
    elif direction == 'speed5':
	speed = 5
        return str(speed)
    elif direction == 'speed10':
	speed = 10
        return str(speed)
    elif direction == 'speed20':
	speed = 20
        return str(speed)

# Function to manually set a motor to a specific pluse width
@app.route("/<motor>/<pulsewidth>")
def manual(motor,pulsewidth):
    if motor == "pan":
        servoPan.set_servo(23, int(pulsewidth))
    elif motor == "tilt":
        servoTilt.set_servo(22, int(pulsewidth))
    return "Moved"

# Clean everything up when the app exits
atexit.register(cleanup)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)


