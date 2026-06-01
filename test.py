import smtplib

print("START")

server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
print("Connected SSL")

server.login("habarnehareej@gmail.com", "magmbcrtcnobssws")
print("Login OK")

server.quit()