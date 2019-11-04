/**************************************************************************
 * BASF2 (Belle Analysis Framework 2)                                     *
 * Copyright(C) 2010 - Belle II Collaboration                             *
 *                                                                        *
 * Author: The Belle II Collaboration                                     *
 * Contributors: Vitalii Popov                                            *
 *                                                                        *
 * This software is provided "as is" without any warranty.                *
 **************************************************************************/


#ifndef EKLMSTRIPEFFMODULE
#define EKLMSTRIPEFFMODULE

#include <framework/core/Module.h>
#include "TFile.h"
#include "TBox.h"
#include "TCanvas.h"
#include "TH2D.h"
#include <framework/datastore/StoreObjPtr.h>
#include <framework/datastore/StoreArray.h>
#include <framework/logging/Logger.h>
#include <eklm/dataobjects/EKLMDigit.h>
#include <eklm/dataobjects/EKLMHit2d.h>
#include <eklm/geometry/GeometryData.h>
#include <eklm/geometry/TransformData.h>
#include <iostream>
#include <set>
#include <klm/dataobjects/KLMDigitEventInfo.h>


namespace Belle2 {

  class EKLMStripEffModule : public Module {
  public:
    EKLMStripEffModule();
    virtual ~EKLMStripEffModule();
    virtual void initialize();
    //! begin run actions                                                                                      
    virtual void beginRun();
    //! Process one event (fill histograms etc)                                                                
    virtual void event();
    //! end run cleanunp                                                                                       
    virtual void endRun();
    //! Terminate at the end of job                                                                            
    virtual void terminate();
  protected:
    long int m_eventCounter;
    TCanvas **** m_cLayer;
    TCanvas **** m_cLayerEff;
    TCanvas *** m_cLayerEff2;
    TH2D *** m_eff2DFound;
    TH2D **** m_eff2DExpected;
    TBox ****** m_strips;
    TBox ****** m_stripsEff;
    int ***** m_stripHits;
    int ***** m_stripHitsEff;
    TH1D *** m_hOccupancy1D;
    HepGeom::Transform3D ***** m_Strip;
    TH1D ** m_hHitsPerLayer_trk;
    TH1D ** m_hHitsPerLayer_notrk;
    TH1D * HitsPerLayerExpected;
    TH1D * TracksPerEvent;
    TH1D * HitsPerEvent1D;
    TH1D * HitsPerEvent2D;
    TH2D * HitsPerEventPerLayer1D;
    TH2D * m_eff2DFound_total_for;
    TH2D * m_eff2DFound_total_back;
    TH1D * HitsRelTime;
    TFile* m_file;
    std::string m_filename;
  private:
    int m_runNumber;
    //! Output filename
    std::string m_outputRootName;

    //! Convert a number of type T into a string
    template <typename T>
    std::string toString(T val)
    {
      std::ostringstream stream;
      stream << val;
      return stream.str();
    }
    
    //m_ElementNumbers = &(EKLM::ElementNumbersSingleton::Instance());
    //    m_GeoDat = &(GeometryData::Instance());
    const EKLM::ElementNumbersSingleton* m_ElementNumbers;
    const EKLM::GeometryData* m_GeoDat;    
    StoreArray<EKLMHit2d> hit2ds;
    StoreArray<EKLMDigit> digits;
    StoreArray<Track> m_Tracks;
    //    StoreArray<klmDigitEventInfo> klmEvInfo;
    StoreArray<KLMDigitEventInfo> m_DigitEventInfos;

  };
}

#endif
