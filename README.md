# PolyFax: An empirical study toolkit on Github projects

# Introduction
![PolyFax](images/polyfax.png)
***
PolyFax provides basic features, including repository crawler, commit classification, and language interaction categorization.
Its precision and recall indicate the possibility of being applied for multiple purposes.
For example, the VCC can be used for empirical analysis and provide abundant training data for machine learning (or deep learning) based vulnerability detectors since the code snippets, issues, or even CVEs of the commits can be retrieved on the results of VCC.
Moreover, it is not limited to the type of language due to the language-independent implementation.

Meanwhile, PolyFax provides a multi-task wrapper in implementation. Hence it enables parallel processes for **Crawler** and **Analyzer** and can retrieve and analyze 10 million commits in 24 hours.

Moreover, PolyFax provides three analyzers of implementation of NBR analysis, including NBR on language selection and vulnerabilities, language interfacing mechanism and vulnerabilities, and single language and vulnerabilities.

Based on the design and implementation of PolyFax, developers or researchers can easily extend or customize the PolyFax based on its object-oriented design.


# Setup PolyFax

Here we present the procedure to setup PolyFax through source code in three steps as below:
1. Check prerequisites. PolyFax is well tested with Python3 under OS ubuntu 18.04; the suggested python version is 3.8+.
2. Download source code through [this](https://github.com/Daybreak2019/PolyFax).
3. Enter directory PolyFax and run [dependence.sh](dependence.sh) to install the necessary dependencies (e.g., fuzzywuzzy, nltk).

Additionaly, we also provide a docker image with all dependences installed (suggested), it contains the data of the paper [On the Vulnerability Proneness of Multilingual Code](https://www.researchgate.net/publication/362080560_On_the_Vulnerability_Proneness_of_Multilingual_Code) with the [link](https://hub.docker.com/r/daybreak2019/fse22_vpomc). Use the command "docker pull daybreak2019/fse22_vpomc" to download the image.

# Use PolyFax
Following sections demonstrate how to use PolyFax with its four primary functionalities: grabbing repositories from GitHub and running the two analyzers of vulnerability-fixing commit, language interaction categorization and NBR analysis.

Before the experiments, execute the following command to get environment ready:
```
docker pull daybreak2019/fse22_vpomc
docker run -itd --name "polyfax" daybreak2019/fse22_vpomc
docker attach polyfax

cd root/ && git clone https://github.com/Daybreak2019/PolyFax && cd PolyFax
```

### Default parameters
PolyFax has a default configure file under [config.ini](Data/Config/config.ini) with the content as below:
1. UserName: the username of GitHub account 
2. Token: the access token of GitHub account
3. TaskNum: the number of process for PolyFax 
4. Languages: the languages the projects should contain
5. Domains: the domains the projects belong to
6. MaxGrabNum: the maximum number of projects to grab

Specifically, {Languages=[]} and {Domains=[]} means the ***Crawler*** would not check languages and domains.
{MaxGrabNum=-1} indicates ***Crawler*** will grab repositories as many as possible.

### Grabbing repositories from GitHub
With the {MaxGrabNum=5} configured for demonstration,
run the following command to grab the repository from GitHub.
In this step, ***Crawler*** will grab the repository profile, clone the repositories, and grab commits to local storage.

```
    python polyfax.py -a crawler
```

The runtime log is similar as:

![PolyFax](images/crawler-log.png)



### Run analyzer of vulnerability-fixing commit categorization (VCC)
When repository profiles and commits are grabbed to local,
users can use the following command to categorize vulnerability-fixing commits:
```
    python polyfax.py -a vcc
```

The runtime log is similar as:

![PolyFax](images/vcc-log.png)



### Run analyzer of language interaction categorization (LIC)
When repository profiles and the sources of repositories are cloned to local in 2.2,
users can use the following command to categorize the projects by language interaction mechanisms:

```
    python polyfax.py -a lic
```

The runtime log is similar as:

![PolyFax](images/lic-log.png)

### Run NBR analysis in paper [On the Vulnerability Proneness of Multilingual Code]
Before run NBR experiments, copy the corresponding data to PolyFax with the following command:
```
cp /root/FSE22_Data/* /root/PolyFax/Data/ -rf
```

#### NBR: \#Secutiry vulnerability vs Language selection
```
    python polyfax.py -a nbr-combo
```
the results correspond to Table 3-5 in the paper.

#### NBR: \#Secutiry vulnerability vs Language interfacing category
```
    python polyfax.py -a nbr-lic
```
the results correspond to Table 6-7 in the paper.

#### NBR: \#Secutiry vulnerability vs Single language
```
    python polyfax.py -a nbr-single
```
the results correspond to Table 8 in the paper.

