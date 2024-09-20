# ARM Development Environment Installation: ARM Keil & Code Composer Studio

2019-01-24

![](https://cdn-images-1.medium.com/max/800/1*-OnOzyRgSQl9x64x2rlT7Q.png)

In the previous article, I said that for this article we’ll switch to writing code, but, I thought it would be more appropriate to give the programs that we can use for coding first. So I’m going to explain what program we’re going to use in this article by deferring the code writing to the next post.

Since we use an ARM-based microcontroller called Stellaris LM4F120 we can use either ARM Keil or Texas Instrument's Code Composer Studio. I will show you how to install both ARM Keil and Code Composer Studio. For programming ARM processors, with C programming language or assembly, both of these two options are pretty good.

## ARM Keil

Follow this section if you want to use ARM Keil as your IDE. Currently, the latest version is **V5.26**, so I am going to continue with it.

Go here for downloading; [ARM Keil](https://www.keil.com/demo/eval/arm.htm#/DOWNLOAD).

*   Right-click on MDK526.EXE and save it to your computer.
*   Wait until downloads completely.

![](https://cdn-images-1.medium.com/max/800/1*qHOMyMZUsogF3sRYWmMW3g.png)

*   Run the MDK526.EXE file and click the next button.

![](https://cdn-images-1.medium.com/max/800/1*C0k2UY-SiiW8Rw_dxL0oPA.png)

*   Accept the Licence Agreement and then click the next button.

![](https://cdn-images-1.medium.com/max/800/1*cf9Du1sYpRVNe945nXdEdg.png)

*   Choose a setup directory.
*   Make sure that there are no spaces in the directory names that go to the installation folder.
*   Click the next button.

![](https://cdn-images-1.medium.com/max/800/1*trDewKPzBdxLTWtCdU2MtA.png)

*   Type the following fields and then click the next button.

![](https://cdn-images-1.medium.com/max/800/1*_hiGJSg7HARBWs3ANEguYA.png)

*   Wait until installation is finished.
*   After you see and click the finish button, you can click the Keil icon and run.

![](https://cdn-images-1.medium.com/max/800/1*yz0436215pz1JdS_hCUy9w.png)

*   Welcome to Arm Keil uVision5!

![](https://cdn-images-1.medium.com/max/800/1*3RiQe8J9xjMq4RYMZ0hnYg.png)

Here is a hint for you. When you want to create a project if you see your device is not in the devices list go to this [link](https://www.keil.com/dd2/pack/) and download a particular device package that is suitable for your microcontroller.

For my particular device, I downloaded the TI family package and executed it.

Now our development medium is ready for new projects.

## Code Composer Studio (CCS)

Follow this section if you want to use Code Composer Studio as your IDE. Currently, the latest version is **8.3.0.00009**, so I am going to continue with it.

Go here for downloading; [CCS](http://processors.wiki.ti.com/index.php/Download_CCS).

*   Make a selection according to your operating system.

![](https://cdn-images-1.medium.com/max/800/1*Sd3JysmRzKddIOU8aLonvg.png)

*   Unzip the WinRAR file that you have downloaded.
*   Double-click on ccs\_setup\_8.3.0.0 and wait for the installation file to open.

![](https://cdn-images-1.medium.com/max/800/1*VeOcmlcbdEMTiGRCDSCMWQ.png)

*   To ensure no problems occur during the installation, make sure that real-time anti-virus programs are turned off before proceeding with the installation.

![](https://cdn-images-1.medium.com/max/800/1*OkvpiiTCF9_x1qra_opx2A.png)

*   Accept the Licence Agreement and then click the next button.

![](https://cdn-images-1.medium.com/max/800/1*UIxxje0PGXTDLEqmLF04Qg.png)

*   Choose a setup directory.
*   Make sure that there are no spaces in the directory names that go to the installation folder.
*   Click the next button.

![](https://cdn-images-1.medium.com/max/800/1*yvX_tWwv4AJGoIkc8oQM8Q.png)

*   Select a product family that matches your own device.

![](https://cdn-images-1.medium.com/max/800/1*JkhTwnfQ65h_F2I63kbPTA.png)

*   Wait until the installation is finished it may take about half an hour.
*   After you see and click the finish button, you can click the CCS icon and run.

![](https://cdn-images-1.medium.com/max/800/1*dA-wEAoGwipiefrLMzfEcQ.png)
![](https://cdn-images-1.medium.com/max/800/1*x5Ao90N-XU57FB52sE_yrA.png)

*   Welcome to Code Composer Studio!

![](https://cdn-images-1.medium.com/max/800/1*cZr_oKL4ucqIbZvO2DEU7A.png)

Now our development medium is ready for new projects. See you in next articles.

Continue reading this series of articles:

*   [Introduction to ARM Architecture](https://erdo.dev/posts/2019-01-24_Introduction-to-ARM-Architecture)
*   [ARM Architecture Instruction Set](https://erdo.dev/posts/2019-07-06_ARM-Architecture-Instruction-Set)

## References

*   [1] [https://developer.arm.com/documentation/kan344/latest/Installation](https://developer.arm.com/documentation/kan344/latest/Installation)
*   [2] [https://software-dl.ti.com/ccs/esd/documents/users_guide_12.2.0/ccs_installation.html](https://software-dl.ti.com/ccs/esd/documents/users_guide_12.2.0/ccs_installation.html)