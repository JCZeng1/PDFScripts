import ROOT as r
import numpy as np
from array import array
#from optparse import OptionParser
import argparse
from ROOT import TH2F,TKDE,kTRUE, TCanvas,TFile, TCanvas, TStyle, TAxis, gStyle, TColor, TPad, TH1F, kBlue,kRed,kSpring,kOrange,kBlack,kGray,kCyan, kViolet, kGreen, gROOT, TLatex, TLine, TF1,TH1D, TGraphErrors, TAxis, kFullCircle, kFALSE, TLegend,kAzure, TGraph
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
        if nMC > 0:
            nComp = (nData) / nMC;
            eComp = eData / nMC;
            h_comp.SetBinContent(bin_x, nComp);
            h_comp.SetBinError(bin_x, eComp);
            #print(h_MC.GetBinCenter(bin_x),nComp)
            pass

        pass
    pass
    return h_comp;

def reweight(h_nom, h_rw):
    h_new = h_rw.Clone()
    h_new.Reset()
    
    ratio = getDataMCRatio(h_nom,h_rw)
    #print(ratio.GetBinContent(1), ratio.GetMean())
    ratio.Fit("pol0","Q")
    weight = ratio.GetFunction("pol0").GetParameter(0)
    #print("fit result weight:",weight)
    arr_val = []
    for bin_x in range(0,h_rw.GetNbinsX()+1):
        con = h_rw.GetBinContent(bin_x)*weight
        err = h_rw.GetBinError(bin_x)
        h_new.SetBinContent(bin_x,con)
        h_new.SetBinError(bin_x,err)
        
    return h_new

sys_names_Sherpa = ["MUR1_MUF1_PDF13000","MUR1_MUF1_PDF25300"]
##sys_names_Sherpa = ["MUR1.0_MUF1.0_PDF13100","MUR1.0_MUF1.0_PDF25200"]

#--------------------------
# User configuration
#--------------------------------------------------------
filename= str(args.dir) #"/eos/user/a/akotsoke/CONDOR_output/merged/2lep.13TeV.mc16ade.ALL.Nominal.r33_12_PF_MjjRW_TagSF_looseTrain_afterFE_PDFweights.root"

#filenameSave = "/eos/home-y/yfhan/forVBSPublic/1lepInputs/TEST.VBS.1lep_local.13TeV.mc16ade.10jun22.root"
filenameSave = "PDFSyst.root"
f=r.TFile(filename,"UPDATE")
f_sys = f.GetDirectory("Systematics/");
f2=r.TFile(filenameSave,"UPDATE")
f2_sys = f2.mkdir("Systematics/");

# sample and associated pdf uncertainties array
samples = ["Z","W" ] #["Z","EW62LepFid-1","W"]
labels = ["SysTheoryPDF_Z","SysTheoryPDF_W"] # each sample comes with its  corresponding ucertainty label
uncertainty_sets = [sys_names_Sherpa,sys_names_Sherpa] # each sample comes with its  corresponding uncertainty array
if int(args.reg) == 0:
        #Resolved
#        regions= ["CRTop", "CRTop_Tight", "CRVjet", "CRVjet_Tight", "SRVBS","SRVBS_Tight", "SRVBS_Tight_HMlvjj1500", "SRVBS_Tight_LMlvjj1500"]
        regions= ["CRVjet_Tight", "SRVBS","SRVBS_Tight"]
        prefix = ["0ptag2pjet_0ptv" for x in regions] #for each region you need to add the corresponding prefix 
        variables = ["DNN","RNN","tagMjj","MVV"]#,"MFullSystem" ] #variables you want to scan
elif int(args.reg) == 1:
        # Merged 
#        regions= ["CRTop_HP", "CRTop_LP", "CRVjet_Merged", "SRVBS_HP","SRVBS_LP", "SRVBS_HP_HMlvJ1500", "SRVBS_HP_LMlvJ1500", "SRVBS_LP_HMlvJ1500", "SRVBS_LP_LMlvJ1500", ]
        regions= ["CRTop_HP", "CRTop_LP", "CRVjet_Merged", "SRVBS_HP","SRVBS_LP"]
        prefix = ["0ptag1pfat0pjet_0ptv" for x in regions]
        variables = ["DNN","RNN","tagMjj","MVV"] #,"MFullSystem"]
else:
        print("Invalid regime to scan")

x_min = [0,0,400,400]
x_max = [1,1,4000,4000]
rebin = [10,10,4,4]



doRebin = True
doNorm = True
##doNorm = False
doConPlots= True

sample_iter=0
for sample in samples:
    var_iter = 0
    for variable in variables:
        region_iter=0
        for region in regions:
            # Get Nominal hist
            keyName=sample+"_"+prefix[region_iter]+"_"+region+"_"+variable
            print("Get Nominal hist for: ",keyName)
            f.cd()
            hist_nom = f.Get(keyName)
            if ("TObject" in str(type(hist_nom))) or (hist_nom.Integral()<=0) :
                print(keyName, " hist doesn't exist")
                continue
            if (hist_nom == None):
                continue

            h_new = hist_nom.Clone()
            h_new.Reset()


            h_new_d = hist_nom.Clone()
            h_new_d.Reset()

            f_sys.cd()
            for binx in range(1,hist_nom.GetNbinsX()+1):
                arr_bin_con = []
                arr_bin_abs = []
                binCenter = hist_nom.GetBinCenter(binx)
                con =  hist_nom.GetBinContent(binx)
                #print(binCenter,con)
                
                # loop over variations
                for j in range(len(uncertainty_sets[sample_iter])):
                    uncertainty_set = uncertainty_sets[sample_iter]
                    variation = variable+"_Sys"+str(uncertainty_set[j])
                    keyName=sample+"_"+prefix[region_iter]+"_"+region+"_"+variation
                    #print("Get variation: ",keyName)
                    hist_var = f_sys.Get(keyName) 
                    if "TObject" in str(type(hist_var)) :
                        print(keyName, " hist doesn't exist")
                        continue  # Skip to the next iteration of the loop

                    ## Reweight problematic pdf sets
                    #if ("PDF269000" in keyName) or ("PDF270000" in keyName):
                    #    #print("Reweighting", keyName)
                    #    hist_var = reweight(hist_nom, hist_var)
                        
                    con_var = hist_var.GetBinContent(binx)
                    abs_diff = math.fabs(con_var - con)
                    diff = con_var - con
                    arr_bin_abs.append(abs_diff)
                    arr_bin_con.append(diff)
                    
                
                # take maximum
                #arr_bin_abs = np.array(arr_bin_abs)
                #print(arr_bin_con)

                # take maximum difference for up uncertainty
                max_v =  np.amax(arr_bin_con)
                index = np.argmax(arr_bin_con)
                #print("up",index,max_v,arr_bin_con[index])

                # take minimum difference for down uncertainty
                min_v =  np.amin(arr_bin_con)
                index_min = np.argmin(arr_bin_con)
                #print("down",index,min_v,arr_bin_con[index_min],con+arr_bin_con[index_min])
                if math.isnan(arr_bin_con[index]):
                    arr_bin_con[index] = 0
                if math.isnan(arr_bin_con[index_min]):
                    arr_bin_con[index_min] = 0


                # set up and down variation values
                h_new.SetBinContent(binx,con+arr_bin_con[index])
                h_new_d.SetBinContent(binx,con+arr_bin_con[index_min])
                #h_new.SetBinError(binx,std)
            
            # write new combined variation hist to output file
            f2_sys.cd()
            var_name = labels[sample_iter] #"qcd_scale"
            out_variation = variable+"_"+str(var_name) #+"__1up"
            out_keyName=sample+"_"+prefix[region_iter]+"_"+region+"_"+out_variation+"__1up"
            out_keyName_d=sample+"_"+prefix[region_iter]+"_"+region+"_"+out_variation+"__1down"
            print("Writing: ", out_keyName)
            ##f_sys.WriteObject(h_new,out_keyName)
            ##f_sys.WriteObject(h_new_d,out_keyName_d)

            # or use this if need to overwrite old hists
            h_new.Write(out_keyName,r.TObject.kOverwrite)
            ##h_new_d.Write(out_keyName_d,r.TObject.kOverwrite)
            
            if doConPlots:
                pdfdir = "./ControlPlots/TheoryPDF/"
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
                    print(variable,rebin[var_iter])
                    hist_nom.Rebin(rebin[var_iter])
                    h_new.Rebin(rebin[var_iter])
                    h_new_d.Rebin(rebin[var_iter])
                    
                if doNorm:
                    hist_nom = getNormhist(hist_nom)
                    h_new = getNormhist(h_new)
                    h_new_d = getNormhist(h_new_d)
                    h_new.GetYaxis().SetTitle("Normalized Entries")
                else:
                    h_new.GetYaxis().SetTitle("Entries")
                    
                h_new.SetStats(0)
                h_new.GetXaxis().SetLabelSize(0.);
                h_new.GetXaxis().SetLabelSize(0.);
                h_new.SetTitle(region)
                h_new.GetXaxis().SetRangeUser(x_min[var_iter],x_max[var_iter])
                #h_new.GetYaxis().SetRangeUser(y_min,y_max)
                h_new.GetXaxis().SetTitle(variables[var_iter])
                #marker style and color
                hist_nom.SetLineColor(kRed)
                hist_nom.SetMarkerColor(kRed)
                hist_nom.SetMarkerStyle(20)
                hist_nom.SetMarkerSize(1.1)
                hist_nom.SetLineWidth(3)
                h_new.SetLineWidth(3)
                h_new_d.SetLineWidth(3)
                h_new.Draw("E0 same")
                hist_nom.Draw("E0 same")
                h_new_d.Draw("E0 same")

                h_new.SetLineColor(kOrange+2)
                h_new_d.SetLineColor(kOrange+2)
                h_new.SetLineStyle(5)

                leg=TLegend(0.45,0.77,0.70,0.90) #x1,y1,x2,y2

                leg.SetBorderSize(0)
                leg.SetFillStyle(0)
                leg.SetTextSize(0.04)
                leg.AddEntry(hist_nom,"Nominal","lep")
                leg.AddEntry(h_new,"Theory PDF - Up","l")
                leg.AddEntry(h_new_d,"Theory PDF - Down","l")
                leg.Draw()
                
                # Ratio 
                P_2.cd()
                h_ratio = getDataMCRatio(h_new,hist_nom)
                h_ratio_d = getDataMCRatio(h_new_d,hist_nom)
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
                h_new_d.SetLineColor(kOrange+2)
                h_ratio.GetYaxis().SetRangeUser(0.9,1.1)
                h_ratio.GetXaxis().SetTitle(variables[var_iter])
                canv.Draw()
                if doNorm:
                    outputname = pdfdir+"/"+out_keyName+"_Norm.pdf"
                    outputname2 = pdfdir+"/"+out_keyName+"_Norm.png"
                else:
                    outputname =  pdfdir+"/"+out_keyName+".pdf"
                    outputname2 =  pdfdir+"/"+out_keyName+".png"
                canv.SaveAs(str(outputname))
                canv.SaveAs(str(outputname2))

            region_iter+=1 
        var_iter+=1
    sample_iter+=1

f.Close()

