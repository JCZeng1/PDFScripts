import ROOT as r
import numpy as np
from array import array
#from optparse import OptionParser
import argparse
from ROOT import TH2F,TKDE, kTRUE,TCanvas,TFile, TCanvas, TStyle, TAxis, gStyle, TColor, TPad, TH1F, kBlue,kRed,kSpring,kBlack,kOrange,kGray,kCyan, kViolet, kGreen, gROOT, TLatex, TLine, TF1,TH1D, TGraphErrors, TAxis, kFullCircle, kFALSE, TLegend,kAzure, TGraph
from math import fabs
import glob
import math
import os

gROOT.SetBatch(kTRUE);

# Argument parser
parser = argparse.ArgumentParser()
parser.add_argument('--dir', help = 'path to root file with pdf uncertainties')
parser.add_argument('--reg', type= int, help = '0 is resolved, 1 is boosted' )
args = parser.parse_args()


# Some functions

# from tobias 
##def reject_outliers(data, nom, m = 1.):
##    size_init = len(data)
##    for i in data:
##        d = abs(i/nom) if nom else 0;
##        if (d > m):
##            data.remove(i)
##    size_final = len(data)
##    if size_final < size_init: print('removed', size_init - size_final, '/' , size_init, 'outliers')
##    return data

def reject_outliers(data, m = 100.):
    size_init = len(data)
    data = np.array(data)
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    data = data[s<m].flatten()
    data = data.tolist()
    size_final = len(data)
    if size_final < size_init: print('removed', size_init - size_final, '/' , size_init, 'outliers')
    return data


def getNormhist(hist):
    h_temp= hist.Clone()
    norm= 1/h_temp.Integral(0,h_temp.GetNbinsX()+1) #TH1::Integral returns the integral of bins in the bin range (default(1,Nbins), to include the Under/Overflow, use h.Integral(0,Nbins+1)
    h_temp.Scale(norm)

    return h_temp

def getDataMCRatio(h_data,h_MC):
    h_comp= h_data.Clone()
    h_comp.Reset()

    for bin_x in range(0,h_comp.GetNbinsX()+1):
        nData = h_data.GetBinContent(bin_x);
        eData = h_data.GetBinError(bin_x);
        nMC = h_MC.GetBinContent(bin_x);
        #print(bin_x,nData,nMC )
        if nMC > 0:
            nComp = (nData) / nMC;
            eComp = eData / nMC;
            #print(bin_x,nComp,eComp)
            h_comp.SetBinContent(bin_x, nComp);
            h_comp.SetBinError(bin_x, eComp);
            pass

        pass
    pass
    return h_comp;

# pdf uncertainties bgd 

sys_names_Sherpa_2 = ["MUR1_MUF1_PDF13000", 
"MUR1_MUF1_PDF269000", 
"MUR1_MUF1_PDF270000", 
"MUR1_MUF1_PDF25300"]
sys_names_top = [
#"PDF set = 25200",
#"PDF set = 13165",
#"PDF set = 90900",
#"PDF set = 265000",
#"PDF set = 266000",
#"PDF set = 303400",
#"0p5muF_PDF4LHC15_NLO_30",
#"2muR_PDF4LHC15_NLO_30",
#"0p5muR_PDF4LHC15_NLO_30",
#"0p5muF_0p5muR_PDF4LHC15_NLO_30",
#"2muF_2muR_PDF4LHC15_NLO_30",
#"0p5muF_2muR_PDF4LHC15_NLO_30",
#"2muF_0p5muR_PDF4LHC15_NLO_30",
#"Var3cUp",
#"Var3cDown",
#"isr:muRfac=2.0_fsr:muRfac=2.0",
#"isr:muRfac=2.0_fsr:muRfac=1.0",
#"isr:muRfac=2.0_fsr:muRfac=0.5",
#"isr:muRfac=1.0_fsr:muRfac=2.0",
#"isr:muRfac=1.0_fsr:muRfac=0.5",
#"isr:muRfac=0.5_fsr:muRfac=2.0",
#"isr:muRfac=0.5_fsr:muRfac=1.0",
#"isr:muRfac=0.5_fsr:muRfac=0.5",
#"isr:muRfac=1.75_fsr:muRfac=1.0",
#"isr:muRfac=1.5_fsr:muRfac=1.0",
#"isr:muRfac=1.25_fsr:muRfac=1.0",
#"isr:muRfac=0.625_fsr:muRfac=1.0",
#"isr:muRfac=0.75_fsr:muRfac=1.0",
#"isr:muRfac=0.875_fsr:muRfac=1.0",
#"hardHi",
#"hardLo",
"PDF set = 90900",
"PDF set = 90901",
"PDF set = 90902",
"PDF set = 90903",
"PDF set = 90904",
"PDF set = 90905",
"PDF set = 90906",
"PDF set = 90907",
"PDF set = 90908",
"PDF set = 90909",
"PDF set = 90910",
"PDF set = 90911",
"PDF set = 90912",
"PDF set = 90913",
"PDF set = 90914",
"PDF set = 90915",
"PDF set = 90916",
"PDF set = 90917",
"PDF set = 90918",
"PDF set = 90919",
"PDF set = 90920",
"PDF set = 90921",
"PDF set = 90922",
"PDF set = 90923",
"PDF set = 90924",
"PDF set = 90925",
"PDF set = 90926",
"PDF set = 90927",
"PDF set = 90928",
"PDF set = 90929",
"PDF set = 90930",
]


sys_names_stop = [
#"PDF set = 25200",
#"PDF set = 13165",
#"PDF set = 90900",
#"PDF set = 90901",
#"PDF set = 90902",
#"PDF set = 90903",
#"PDF set = 90904",
#"PDF set = 90905",
#"PDF set = 90906",
#"PDF set = 90907",
#"PDF set = 90908",
#"PDF set = 90909",
#"PDF set = 90910",
#"PDF set = 90911",
#"PDF set = 90912",
#"PDF set = 90913",
#"PDF set = 90914",
#"PDF set = 90915",
#"PDF set = 90916",
#"PDF set = 90917",
#"PDF set = 90918",
#"PDF set = 90919",
#"PDF set = 90920",
#"PDF set = 90921",
#"PDF set = 90922",
#"PDF set = 90923",
#"PDF set = 90924",
#"PDF set = 90925",
#"PDF set = 90926",
#"PDF set = 90927",
#"PDF set = 90928",
#"PDF set = 90929",
#"PDF set = 90930",
#"Var3cUp",
#"Var3cDown",
#"isr:muRfac=2.0_fsr:muRfac=2.0",
#"isr:muRfac=2.0_fsr:muRfac=1.0",
#"isr:muRfac=2.0_fsr:muRfac=0.5",
#"isr:muRfac=1.0_fsr:muRfac=2.0",
#"isr:muRfac=1.0_fsr:muRfac=0.5",
#"isr:muRfac=0.5_fsr:muRfac=2.0",
#"isr:muRfac=0.5_fsr:muRfac=1.0",
#"isr:muRfac=0.5_fsr:muRfac=0.5",
#"isr:muRfac=1.75_fsr:muRfac=1.0",
#"isr:muRfac=1.5_fsr:muRfac=1.0",
#"isr:muRfac=1.25_fsr:muRfac=1.0",
#"isr:muRfac=0.625_fsr:muRfac=1.0",
#"isr:muRfac=0.75_fsr:muRfac=1.0",
#"isr:muRfac=0.875_fsr:muRfac=1.0",
#"isr:muRfac=1.0_fsr:muRfac=1.75",
#"isr:muRfac=1.0_fsr:muRfac=1.5",
#"isr:muRfac=1.0_fsr:muRfac=1.25",
#"isr:muRfac=1.0_fsr:muRfac=0.625",
#"isr:muRfac=1.0_fsr:muRfac=0.75",
#"isr:muRfac=1.0_fsr:muRfac=0.875",
#"hardHi",
#"hardLo",
#"isr:PDF:plus",
#"isr:PDF:minus",
"PDF set = 260001",
"PDF set = 260002",
"PDF set = 260003",
"PDF set = 260004",
"PDF set = 260005",
"PDF set = 260006",
"PDF set = 260007",
"PDF set = 260008",
"PDF set = 260009",
"PDF set = 260010",
"PDF set = 260011",
"PDF set = 260012",
"PDF set = 260013",
"PDF set = 260014",
"PDF set = 260015",
"PDF set = 260016",
"PDF set = 260017",
"PDF set = 260018",
"PDF set = 260019",
"PDF set = 260020",
"PDF set = 260021",
"PDF set = 260022",
"PDF set = 260023",
"PDF set = 260024",
"PDF set = 260025",
"PDF set = 260026",
"PDF set = 260027",
"PDF set = 260028",
"PDF set = 260029",
"PDF set = 260030",
"PDF set = 260031",
"PDF set = 260032",
"PDF set = 260033",
"PDF set = 260034",
"PDF set = 260035",
"PDF set = 260036",
"PDF set = 260037",
"PDF set = 260038",
"PDF set = 260039",
"PDF set = 260040",
"PDF set = 260041",
"PDF set = 260042",
"PDF set = 260043",
"PDF set = 260044",
"PDF set = 260045",
"PDF set = 260046",
"PDF set = 260047",
"PDF set = 260048",
"PDF set = 260049",
"PDF set = 260050",
"PDF set = 260051",
"PDF set = 260052",
"PDF set = 260053",
"PDF set = 260054",
"PDF set = 260055",
"PDF set = 260056",
"PDF set = 260057",
"PDF set = 260058",
"PDF set = 260059",
"PDF set = 260060",
"PDF set = 260061",
"PDF set = 260062",
"PDF set = 260063",
"PDF set = 260064",
"PDF set = 260065",
"PDF set = 260066",
"PDF set = 260067",
"PDF set = 260068",
"PDF set = 260069",
"PDF set = 260070",
"PDF set = 260071",
"PDF set = 260072",
"PDF set = 260073",
"PDF set = 260074",
"PDF set = 260075",
"PDF set = 260076",
"PDF set = 260077",
"PDF set = 260078",
"PDF set = 260079",
"PDF set = 260080",
"PDF set = 260081",
"PDF set = 260082",
"PDF set = 260083",
"PDF set = 260084",
"PDF set = 260085",
"PDF set = 260086",
"PDF set = 260087",
"PDF set = 260088",
"PDF set = 260089",
"PDF set = 260090",
"PDF set = 260091",
"PDF set = 260092",
"PDF set = 260093",
"PDF set = 260094",
"PDF set = 260095",
"PDF set = 260096",
"PDF set = 260097",
"PDF set = 260098",
"PDF set = 260099",
"PDF set = 260100",
]
# NNPDF set
sys_names_Sherpa = [ 
"MUR1_MUF1_PDF261001", 
"MUR1_MUF1_PDF261002",
"MUR1_MUF1_PDF261003", 
"MUR1_MUF1_PDF261004", 
"MUR1_MUF1_PDF261005",
"MUR1_MUF1_PDF261006",
"MUR1_MUF1_PDF261007",
"MUR1_MUF1_PDF261008",
"MUR1_MUF1_PDF261009",
"MUR1_MUF1_PDF261010",
"MUR1_MUF1_PDF261011",
"MUR1_MUF1_PDF261012",
"MUR1_MUF1_PDF261013",
"MUR1_MUF1_PDF261014",
"MUR1_MUF1_PDF261015",
"MUR1_MUF1_PDF261016",
"MUR1_MUF1_PDF261017",
"MUR1_MUF1_PDF261018",
"MUR1_MUF1_PDF261019",
"MUR1_MUF1_PDF261020",
"MUR1_MUF1_PDF261021",
"MUR1_MUF1_PDF261022",
"MUR1_MUF1_PDF261023",
"MUR1_MUF1_PDF261024",
"MUR1_MUF1_PDF261025",
"MUR1_MUF1_PDF261026",
"MUR1_MUF1_PDF261027",
"MUR1_MUF1_PDF261028",
"MUR1_MUF1_PDF261029",
"MUR1_MUF1_PDF261030",
"MUR1_MUF1_PDF261031",
"MUR1_MUF1_PDF261032",
"MUR1_MUF1_PDF261033", 
"MUR1_MUF1_PDF261034", 
"MUR1_MUF1_PDF261035", 
"MUR1_MUF1_PDF261036", 
"MUR1_MUF1_PDF261037", 
"MUR1_MUF1_PDF261038", 
"MUR1_MUF1_PDF261039", 
"MUR1_MUF1_PDF261040", 
"MUR1_MUF1_PDF261041", 
"MUR1_MUF1_PDF261042", 
"MUR1_MUF1_PDF261043", 
"MUR1_MUF1_PDF261044", 
"MUR1_MUF1_PDF261045", 
"MUR1_MUF1_PDF261046", 
"MUR1_MUF1_PDF261047", 
"MUR1_MUF1_PDF261048", 
"MUR1_MUF1_PDF261049", 
"MUR1_MUF1_PDF261050", 
"MUR1_MUF1_PDF261051", 
"MUR1_MUF1_PDF261052", 
"MUR1_MUF1_PDF261053", 
"MUR1_MUF1_PDF261054",
"MUR1_MUF1_PDF261055", 
"MUR1_MUF1_PDF261056", 
"MUR1_MUF1_PDF261057",
"MUR1_MUF1_PDF261058", 
"MUR1_MUF1_PDF261059",
"MUR1_MUF1_PDF261060",
"MUR1_MUF1_PDF261061", 
"MUR1_MUF1_PDF261062", 
"MUR1_MUF1_PDF261063", 
"MUR1_MUF1_PDF261064", 
"MUR1_MUF1_PDF261065", 
"MUR1_MUF1_PDF261066", 
"MUR1_MUF1_PDF261067", 
"MUR1_MUF1_PDF261068", 
"MUR1_MUF1_PDF261069", 
"MUR1_MUF1_PDF261070", 
"MUR1_MUF1_PDF261071", 
"MUR1_MUF1_PDF261072", 
"MUR1_MUF1_PDF261073",
"MUR1_MUF1_PDF261074", 
"MUR1_MUF1_PDF261075", 
"MUR1_MUF1_PDF261076",
"MUR1_MUF1_PDF261077", 
"MUR1_MUF1_PDF261078", 
"MUR1_MUF1_PDF261079", 
"MUR1_MUF1_PDF261080", 
"MUR1_MUF1_PDF261081", 
"MUR1_MUF1_PDF261082", 
"MUR1_MUF1_PDF261083", 
"MUR1_MUF1_PDF261084", 
"MUR1_MUF1_PDF261085", 
"MUR1_MUF1_PDF261086", 
"MUR1_MUF1_PDF261087", 
"MUR1_MUF1_PDF261088", 
"MUR1_MUF1_PDF261089", 
"MUR1_MUF1_PDF261090", 
"MUR1_MUF1_PDF261091", 
"MUR1_MUF1_PDF261092", 
"MUR1_MUF1_PDF261093", 
"MUR1_MUF1_PDF261094", 
"MUR1_MUF1_PDF261095", 
"MUR1_MUF1_PDF261096",
"MUR1_MUF1_PDF261097",
"MUR1_MUF1_PDF261098",
"MUR1_MUF1_PDF261099", 
"MUR1_MUF1_PDF261100",
]


sys_names_signal =[
"PDF=260000 MemberID=86", 
"PDF=260000 MemberID=78",
"PDF=260000 MemberID=14",
"PDF=260000 MemberID=38", 
"PDF=260000 MemberID=77", 
"PDF=260000 MemberID=67", 
"PDF=260000 MemberID=46", 
"PDF=260000 MemberID=57", 
"PDF=260000 MemberID=30", 
"PDF=260000 MemberID=26", 
"PDF=260000 MemberID=81", 
"PDF=260000 MemberID=79", 
"PDF=260000 MemberID=15", 
"PDF=260000 MemberID=6",  
"PDF=260000 MemberID=39", 
"PDF=260000 MemberID=49", 
#"dyn_scale_choice=HT", 
#"dyn_scale_choice=sum pt", 
"PDF=260000 MemberID=66", 
"PDF=260000 MemberID=70", 
"PDF=260000 MemberID=54", 
"PDF=260000 MemberID=31", 
"PDF=260000 MemberID=41", 
"PDF=260000 MemberID=94", 
"PDF=260000 MemberID=80", 
"PDF=260000 MemberID=92", 
"PDF=260000 MemberID=5", 
"PDF=260000 MemberID=12", 
"PDF=260000 MemberID=65", 
"PDF=260000 MemberID=48", 
"PDF=260000 MemberID=55", 
"PDF=260000 MemberID=32", 
"PDF=260000 MemberID=89", 
"PDF=260000 MemberID=24",
"PDF=260000 MemberID=71", 
"PDF=260000 MemberID=40", 
"PDF=260000 MemberID=95", 
"PDF=260000 MemberID=4", 
"PDF=260000 MemberID=7", 
#"dyn_scale_choice=sqrts", 
"PDF=260000 MemberID=9", 
"PDF=260000 MemberID=35", 
"PDF=260000 MemberID=64", 
"PDF=260000 MemberID=52", 
"PDF=260000 MemberID=33", 
"PDF=260000 MemberID=88", 
"PDF=260000 MemberID=23", 
"PDF=260000 MemberID=25", 
"PDF=260000 MemberID=93", 
"PDF=260000 MemberID=43", 
"PDF=260000 MemberID=3",  
"PDF=260000 MemberID=90", 
"PDF=260000 MemberID=10", 
"PDF=260000 MemberID=73", 
"PDF=260000 MemberID=53", 
"PDF=260000 MemberID=63", 
"PDF=260000 MemberID=42", 
"PDF=260000 MemberID=100", 
"PDF=260000 MemberID=22", 
"PDF=260000 MemberID=34", 
"PDF=260000 MemberID=83", 
"PDF=260000 MemberID=18", 
"PDF=260000 MemberID=2", 
"PDF=260000 MemberID=91", 
"PDF=260000 MemberID=69", 
"PDF=260000 MemberID=29", 
"PDF=260000 MemberID=13", 
"PDF=260000 MemberID=11", 
"PDF=260000 MemberID=62", 
"PDF=260000 MemberID=50", 
"PDF=260000 MemberID=21", 
"PDF=260000 MemberID=74", 
"PDF=260000 MemberID=19", 
"PDF=260000 MemberID=45",  
"PDF=260000 MemberID=98", 
"PDF=260000 MemberID=58", 
"PDF=260000 MemberID=82", 
"PDF=260000 MemberID=68", 
"PDF=260000 MemberID=96", 
"PDF=260000 MemberID=84", 
"PDF=260000 MemberID=1", 
"PDF=260000 MemberID=28",  
"PDF=260000 MemberID=16",  
"PDF=260000 MemberID=51", 
"PDF=260000 MemberID=37", 
"PDF=260000 MemberID=99", 
"PDF=260000 MemberID=20", 
"PDF=260000 MemberID=75", 
"PDF=260000 MemberID=85", 
"PDF=260000 MemberID=61", 
"PDF=260000 MemberID=44", 
"PDF=260000 MemberID=59", 
"PDF=260000 MemberID=36", 
"PDF=260000 MemberID=72", 
"PDF=260000 MemberID=97", 
"PDF=260000 MemberID=87", 
"PDF=260000 MemberID=8", 
"PDF=260000 MemberID=17", 
"PDF=260000 MemberID=76", 
"PDF=260000 MemberID=60", 
"PDF=260000 MemberID=47", 
"PDF=260000 MemberID=56",
"PDF=260000 MemberID=27" ]

# following recommendations from https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/PmgSystematicUncertaintyRecipes#Scale_uncertainties
sys_as_Sherpa = [ "MUR1_MUF1_PDF269000","MUR1_MUF1_PDF270000"] #269000 ->as_0117  270000-> as_0119, #nominal is as_0118

# PDF Uncertainties
#--------------------------
# User configuration
#--------------------------------------------------------
filename= str(args.dir) #"/eos/user/a/akotsoke/CONDOR_output/merged/2lep.13TeV.mc16ade.ALL.Nominal.r33_12_PF_MjjRW_TagSF_looseTrain_afterFE_PDFweights.root"
f=r.TFile(filename,"UPDATE")
f_sys = f.GetDirectory("Systematics/");
#filenameSave = "/eos/home-y/yfhan/forVBSPublic/1lepInputs/Histograms.VBS.1lep_local.13TeV.mc16ade.10jun22.root"
filenameSave = "PDFSyst.root"
f2=r.TFile(filenameSave,"UPDATE")
f2_sys = f2.mkdir("Systematics/");

# sample and associated pdf uncertainties array
samples = ["EW6lvqqFidA", "EW6lvqqFidC", "EW6lvqqFidD", "W","Z", "WZ", "WW", "ZZ", "ttbar", "stopWt","stops","stopt"]
labels = ["SysTheoryPDF_NNPDF_VBS","SysTheoryPDF_NNPDF_VBS","SysTheoryPDF_NNPDF_VBS","SysTheoryPDF_NNPDF_W","SysTheoryPDF_NNPDF_Z","SysTheoryPDF_NNPDF_VV","SysTheoryPDF_NNPDF_VV","SysTheoryPDF_NNPDF_VV","SysTheoryPDF_NNPDF_ttbar","SysTheoryPDF_NNPDF_stop","SysTheoryPDF_NNPDF_stop","SysTheoryPDF_NNPDF_stop"] # each sample comes with its  corresponding ucertainty label
uncertainty_sets = [
sys_names_signal,sys_names_signal,sys_names_signal,
sys_names_Sherpa,sys_names_Sherpa,sys_names_Sherpa,sys_names_Sherpa,sys_names_Sherpa,
sys_names_top,sys_names_stop,sys_names_stop,sys_names_stop,
]
#samples = ["EW6lvqqFidA", "EW6lvqqFidC", "EW6lvqqFidD"]
#labels = ["SysTheoryPDF_NNPDF_VBS","SysTheoryPDF_NNPDF_VBS","SysTheoryPDF_NNPDF_VBS"]
#uncertainty_sets = [sys_names_signal,sys_names_signal,sys_names_signal]

if int(args.reg) == 0:
        #Resolved
        regions= ["CRTop_Tight", "CRVjet", "CRVjet_Tight", "SRVBS","SRVBS_Tight", "SRVBS_Tight_HMlvjj1500", "SRVBS_Tight_LMlvjj1500"]
        prefix = ["0ptag2pjet_0ptv", "0ptag2pjet_0ptv", "0ptag2pjet_0ptv", "0ptag2pjet_0ptv", "0ptag2pjet_0ptv", "0ptag2pjet_0ptv", "0ptag2pjet_0ptv"] #for each region you need to add the corresponding prefix 
        variables = ["DNN","RNN","tagMjj","MVV"]#,"MFullSystem" ] #variables you want to scan
elif int(args.reg) == 1:
        # Merged 
        regions= ["CRTop_HP", "CRTop_LP", "CRVjet_Merged", "SRVBS_HP","SRVBS_LP", "SRVBS_HP_HMlvJ1500", "SRVBS_HP_LMlvJ1500", "SRVBS_LP_HMlvJ1500", "SRVBS_LP_LMlvJ1500", ]
        prefix = ["0ptag1pfat0pjet_0ptv","0ptag1pfat0pjet_0ptv","0ptag1pfat0pjet_0ptv","0ptag1pfat0pjet_0ptv","0ptag1pfat0pjet_0ptv", "0ptag1pfat0pjet_0ptv","0ptag1pfat0pjet_0ptv", "0ptag1pfat0pjet_0ptv","0ptag1pfat0pjet_0ptv"]
        variables = ["DNN","RNN","tagMjj","MVV"] #,"MFullSystem"]
else:
        print("Invalid regime to scan")


x_min = [0,400]
x_max = [1,4000]
rebin = [3,30]

doConPlots= False
doRebin = False
doNorm = False
#------------------------------------------------------------------------------------

sample_iter=0
for sample in samples:
    var_iter = 0
    for variable in variables:
        region_iter=0
        for region in regions:
            f_sys.cd()
            # Get Nominal hist
            keyName=sample+"_"+prefix[region_iter]+"_"+region+"_"+variable
            print("Get Nominal hist for: ",keyName)
            hist_nom = f.Get(keyName)
            if ("TObject" in str(type(hist_nom))) or (hist_nom.Integral()<=0) :
                print(keyName, " hist doesn't exist")
                continue
            if hist_nom == None:
                continue 
            h_new_up = hist_nom.Clone()
            h_new_up.Reset()
            h_new_down = hist_nom.Clone()
            h_new_down.Reset()

            # a_s variations 
            as_up_keyName = sample+"_"+prefix[region_iter]+"_"+region+"_"+variable+"_Sys"+str(sys_as_Sherpa[1])
            as_down_keyName = sample+"_"+prefix[region_iter]+"_"+region+"_"+variable+"_Sys"+str(sys_as_Sherpa[0])
            hist_as_up = f_sys.Get(as_up_keyName)
            hist_as_down = f_sys.Get(as_down_keyName) 
            if ("TObject" in str(type(hist_as_up))) or ("TObject" in str(type(hist_as_down))) :
                print(as_up_keyName, " hist doesn't exist") # bug on name reported here
		#continue

            for binx in range(0,hist_nom.GetNbinsX()+1):
                arr_bin_con = []
                binCenter = hist_nom.GetBinCenter(binx)
                con =  hist_nom.GetBinContent(binx)
                #print(binCenter,con)
                
                if "EW" in sample or "ttbar" in sample or "stop" in sample:
                    delta_as = 0.
                else:
                    delta_as = (hist_as_down.GetBinContent(binx) - hist_as_up.GetBinContent(binx) )/2

                #print(hist_as_down.GetBinContent(binx),hist_as_up.GetBinContent(binx))
                
                # loop over variations
                for j in range(len(uncertainty_sets[sample_iter])):
                    uncertainty_set = uncertainty_sets[sample_iter]
                    variation = variable+"_Sys"+str(uncertainty_set[j])
                    keyName=sample+"_"+prefix[region_iter]+"_"+region+"_"+variation

                    #print("Get variation: ",keyName)
                    hist_var = f_sys.Get(keyName) 
                    if "TObject" in str(type(hist_var)) :
                        print(keyName, " hist doesn't exist")
                        
                    con_var = hist_var.GetBinContent(binx)
##                    if not abs(con_var - con) > con:
                    arr_bin_con.append(con_var)


                # tofitsch: remove outliers
                arr_bin_con = reject_outliers(arr_bin_con)
                # take mean and std
                arr_bin_con = np.array(arr_bin_con)
                #print(arr_bin_con)
                mean = np.mean(arr_bin_con)
                std = np.std(arr_bin_con)
                combined_unc = math.sqrt(std*std + delta_as*delta_as)
                #print(binx,delta_as,std,combined_unc )
                if math.isnan(combined_unc):
                    combined_unc = 0

                # h_new_up.SetBinContent(binx,con+std)
                # h_new_down.SetBinContent(binx,con-std)
                h_new_up.SetBinContent(binx,con+combined_unc)
                h_new_down.SetBinContent(binx,con-combined_unc)

            
            # write new combined variation hist to output file
            f2_sys.cd()
            var_name = labels[sample_iter] #"PDF_internal"
            out_variation_up = variable+"_"+str(var_name)+"__1up"
            out_keyName_up=sample+"_"+prefix[region_iter]+"_"+region+"_"+out_variation_up
            print("Writing: ", out_keyName_up)
            #f_sys.WriteObject(h_new_up,out_keyName_up)
            
            out_variation_down = variable+"_"+str(var_name)+"__1down"
            out_keyName_down=sample+"_"+prefix[region_iter]+"_"+region+"_"+out_variation_down
            print("Writing: ", out_keyName_down)
            #f_sys.WriteObject(h_new_down,out_keyName_down)
            # or use this if need to overwrite old hists
            h_new_up.Write(out_keyName_up,r.TObject.kOverwrite)
            h_new_down.Write(out_keyName_down,r.TObject.kOverwrite)

            if doConPlots:
                pdfdir = "./ControlPlots/NNPDF/"
                if not os.path.exists(pdfdir) :
                    os.makedirs(pdfdir)
        
                canv=TCanvas("","",60,60,600,600)
                P_1 = TPad("Hists","", 0, 0.35, 0.94, 1);
                P_2 =TPad("Data/Bgd","", 0, 0.1, 0.94, 0.35); #xmin,ymin,xmax,ymax

                P_1.Draw();
                P_2.Draw();

                P_1.SetBottomMargin(0.02);
                P_1.SetTopMargin(0.07);
                P_1.SetRightMargin(0.15);
                P_1.SetLeftMargin(0.15);
    
                P_2.SetTopMargin(0.07);
                P_2.SetBottomMargin(0.3);
                P_2.SetRightMargin(0.15);
                P_2.SetLeftMargin(0.15);
    
                P_1.cd()
        
                if doRebin:
                    #print(variable,rebin[var_iter])
                    hist_nom.Rebin(rebin[var_iter])
                    h_new_up.Rebin(rebin[var_iter])
                    h_new_down.Rebin(rebin[var_iter])
                    
                if doNorm:
                    hist_nom = getNormhist(hist_nom)
                    h_new_up = getNormhist(h_new_up)
                    h_new_down =getNormhist(h_new_down)
                    hist_nom.GetYaxis().SetTitle("Normalized Entries")
                else:
                    hist_nom.GetYaxis().SetTitle("Entries")
                    
                hist_nom.SetStats(0)
                hist_nom.GetXaxis().SetLabelSize(0.);
                hist_nom.GetXaxis().SetLabelSize(0.);
                hist_nom.SetTitle(region)
                hist_nom.GetXaxis().SetRangeUser(x_min[var_iter],x_max[var_iter])
                #hist_nom.GetYaxis().SetRangeUser(y_min,y_max)
                hist_nom.GetXaxis().SetTitle(variables[var_iter])
                #marker style and color
                hist_nom.SetLineColor(kRed)
                hist_nom.SetMarkerColor(kRed)
                hist_nom.SetMarkerStyle(20)
                hist_nom.SetMarkerSize(1.1)
                hist_nom.SetLineWidth(3)
                h_new_up.SetLineWidth(3)
                h_new_down.SetLineWidth(3)
                hist_nom.Draw("E0 same")
                h_new_up.Draw("E0 same")
                h_new_down.Draw("E0 same")
                h_new_up.SetLineColor(kOrange+2)
                h_new_down.SetLineColor(kOrange+2)
                h_new_down.SetLineStyle(5)

                leg=TLegend(0.45,0.77,0.70,0.90) #x1,y1,x2,y2

                leg.SetBorderSize(0)
                leg.SetFillStyle(0)
                leg.SetTextSize(0.04)
                leg.AddEntry(hist_nom,"Nominal","lep")
                leg.AddEntry(h_new_up,"NNPDF MC replicas - up","l")
                leg.AddEntry(h_new_down,"NNPDF MC replicas - down","l")
                leg.Draw()
                
                # Ratio 
                P_2.cd()
                h_ratio = getDataMCRatio(h_new_up,hist_nom)
                h_ratio_d = getDataMCRatio(h_new_down,hist_nom)
                h_ratio.SetTitle("")
                h_ratio.GetYaxis().SetTitle("#pm#sigma/Nominal")
                h_ratio.GetYaxis().SetTitleSize(0.14);
                h_ratio.GetYaxis().SetTitleOffset(0.3);
                h_ratio.GetYaxis().SetLabelSize(0.1);
                h_ratio.GetXaxis().SetTitleSize(0.14);
                h_ratio.GetXaxis().SetTitleOffset(1.1);
                h_ratio.GetXaxis().SetLabelSize(0.12);
                h_ratio.SetStats(0)
                h_ratio.SetLineWidth(3)
                h_ratio_d.SetLineWidth(3)
                h_ratio.Draw("hist")
                h_ratio_d.Draw("hist same")
                h_ratio.GetYaxis().SetRangeUser(0.9,1.1)
                h_ratio.GetXaxis().SetTitle(variables[var_iter])
                canv.Draw()
                if doNorm:
                    outputname = pdfdir+"/"+out_keyName_up+"_Norm.png"
                else:
                    outputname = pdfdir+"/"+out_keyName_up+".png"
                #canv.SaveAs(str(outputname)+".png")
                canv.SaveAs(str(outputname))
                

            region_iter+=1 
        var_iter+=1
    sample_iter+=1


#print(h_new.Integral())
f.Close()


