<!-- dx-header -->
# PSMC pipeline (DNAnexus Platform App)

Create a linear calibrated PSMC output from consensus sequences for 2 samples

This is the source code for an app that runs on the DNAnexus Platform.
For more information about how to run or modify it, see
http://wiki.dnanexus.com/.
<!-- /dx-header -->



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

* **Consensus sequence file 1** ``cons1``: ``file``
* **Consensus sequence file 2** ``cons2``: ``file``
* **Window size** ``skip``: ``int``
* **Maximum time in years** ``timemax``: ``float``
* **Output root filename** ``outroot``: ``string``

## Outputs

* **PSMC fasta file** ``outfile1``: ``file``
* **Recalibrated linear PSMC file** ``outfile2``: ``file``