javac -cp ../lib/vboxjws.jar:../lib/commons-logging-1.1.3.jar:../lib/httpclient-4.3.1.jar:../lib/httpcore-4.3.jar eu/citizencyberlab/icstm/cg/ClientVboxLauncher.java
jar -cvf vboxlauncher.jar .
mv vboxlauncher.jar ../../prototype-django/citizengrid/static/vbox-launcher
jarsigner ../../prototype-django/citizengrid/static/vbox-launcher/vboxlauncher.jar citizengrid --storepass citizengrid

