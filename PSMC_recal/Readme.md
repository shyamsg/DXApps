<!-- dx-header -->
# PSMC_recal (DNAnexus Platform App)

Linear recalibration rerun of PSMC

This is the source code for an app that runs on the DNAnexus Platform.
For more information about how to run or modify it, see
http://wiki.dnanexus.com/.
<!-- /dx-header -->

Runs the recalibrated version of PSMC assuming that the paramter files have been generated.

<!--
TODO: This app directory was automatically generated by dx-app-wizard;
please edit this Readme.md file to include essential documentation about
your app that would be helpful to users. (Also see the
Readme.developer.md.) Once you're done, you can remove these TODO
comments.

For more info, see http://wiki.dnanexus.com/Developer-Portal.
-->

<!--
TODO: Fill in additional info about how to use each input and output
below.
-->

## Inputs

* **PSMC filename** ``psmcfa``: ``file``
* **Output filename** ``outname``: ``string``
* **Maximum PSMC time after recalibration** ``timemax``: ``float``
* **Recalibrated paramter filename** ``parfile``: ``file``

## Outputs

* **Output PSMC file** ``outfile``: ``file``
