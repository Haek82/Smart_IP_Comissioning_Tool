# Smart_IP_Comissioning_Tool
Commissioning tool for Genelec Smart IP Speakers.

The program uses an excel spreadsheet as an "Master List" for desired configuration data.<br>
Program browses for mDNS querrys on _smart_ip.tcp service and discovers speakers in this manner.<br>
Once discovered the program will compare the speaker configuration to the master list, <br>if confiugaration differs from master list the program will prompt you if you want to update config.<br>
If update is run and completed the program will write speaker mac address and Dante name to maste list.<br>
<h3>NOTE !</h3>
Excel file can not be open during the time program writes to master list.

Binary releases can be found on <a href="https://github.com/Haek82/Smart_IP_Comissioning_Tool/releases">Releases</a>
