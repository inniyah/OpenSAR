import sys,os
import xml.etree.ElementTree as ET
from .GenFee import GenFee
from .GenEa import GenEa

__all__ = ['GenNvM']


__Header = \
"""/*
* Configuration of module: NvM
*
* Created by:   parai          
* Copyright:    (C)parai@foxmail.com  
*
* Configured for (MCU):    MinGW ...
*
* Module vendor:           ArcCore
* Generator version:       2.0.34
*
* Generated by easySAR Studio (https://github.com/parai/OpenSAR)
* Current only for NvM+Fee.
*/
"""

__dir = '.'
__root = None

def GAGet(what,which):
    try:
        return what.attrib[which]
    except:
        if(which == 'BlockSize'):
            Size = 0
            for data in what.find('DataList'):
                if(data.attrib['type']=='uint32'):
                    Size += 4
                elif(data.attrib['type']=='uint16'):
                    Size += 2
                elif(data.attrib['type']=='uint8'):
                    Size += 1
                elif(data.attrib['type']=='uint32_n'):
                    Size += 4*tInt(data.attrib['size'])
                elif(data.attrib['type']=='uint16_n'):
                    Size += 2*tInt(data.attrib['size'])
                elif(data.attrib['type']=='uint8_n'):
                    Size += tInt(data.attrib['size'])
            return Size
        else:
            return None    
def GLGet(what,which = None):
    """ Gen Get List
        Get A Special List []
    """
    global __root
    try:
        return __root.find(what)
    except:
        try:
            return what.find(which)
        except:
            return None
    
def GenNvM(wfxml):
    global __dir,__root
    __root = ET.parse(wfxml).getroot();
    __dir = os.path.dirname(wfxml)
    GenFee(wfxml)
    GenEa(wfxml)
    GenH()
    GenC()
    print('>>> Gen NvM DONE <<<')


def tInt(strnum):
    if(strnum.find('0x')!=-1 or strnum.find('0X')!=-1):
        return int(strnum,16)
    else:
        return int(strnum,10)

def GenH():
    global __dir
    fp = open('%s/NvM_Cfg.h'%(__dir),'w')
    fp.write(__Header)  
    fp.write("""
#ifndef NVM_CFG_H_
#define NVM_CFG_H_

#include "NvM_Types.h"
#include "NvM_ConfigTypes.h"

#define NVM_DEV_ERROR_DETECT            STD_ON
#define NVM_VERSION_INFO_API            STD_ON
#define NVM_SET_RAM_BLOCK_STATUS_API    STD_OFF

#define NVM_API_CONFIG_CLASS            NVM_API_CONFIG_CLASS_2     // Class 1-3
#define NVM_COMPILED_CONFIG_ID          0                          // 0..65535
#define NVM_CRC_NUM_OF_BYTES            0                          // 1..65535
#define NVM_DATASET_SELECTION_BITS      0                          // 0..8
#define NVM_DRV_MODE_SWITCH             STD_OFF                    // OFF = SLOW, ON = FAST
#define NVM_DYNAMIC_CONFIGURATION       STD_OFF                    // OFF..ON
#define NVM_JOB_PRIORIZATION            STD_OFF                    // OFF..ON
#define NVM_MAX_NUMBER_OF_WRITE_RETRIES 2                          // 0..7
#define NVM_POLLING_MODE                STD_OFF                    // OFF..ON
#define NVM_SIZE_IMMEDIATE_JOB_QUEUE    8                          // 1..255
#define NVM_SIZE_STANDARD_JOB_QUEUE     8                          // 1..255\n\n""")
    max_block_size = 0
    for block in GLGet('FeeBlockList'):
        if(GAGet(block,'BlockSize')>max_block_size):
            max_block_size = GAGet(block,'BlockSize')
    for block in GLGet('EaBlockList'):
        if(GAGet(block,'BlockSize')>max_block_size):
            max_block_size = GAGet(block,'BlockSize')            
    fp.write('#define NVM_MAX_BLOCK_LENGTH %s\n\n'%(max_block_size))
    fp.write('#define NVM_NUM_OF_NVRAM_BLOCKS %s\n\n'%(len(GLGet('FeeBlockList'))+len(GLGet('EaBlockList'))))
    #Zero Id reserved by NvM
    Id = 1
    for block in GLGet('FeeBlockList'):
        fp.write('#define NVM_BLOCK_ID_%s %s\n'%(GAGet(block,'name'),Id))
        Id += 1
    for block in GLGet('EaBlockList'):
        fp.write('#define NVM_BLOCK_ID_%s %s\n'%(GAGet(block,'name'),Id))
        Id += 1        
    #for each block, generate a readable memory map type
    for block in GLGet('FeeBlockList'):
        cstr = '\ntypedef struct{\n'
        for data in GLGet(block,'DataList'):
            if( GAGet(data,'type') == 'uint32' or 
                GAGet(data,'type') == 'uint16' or 
                GAGet(data,'type') == 'uint8'):
                cstr += '\t%s _%s;\n'%(GAGet(data,'type'),GAGet(data,'name'))
            else:
                cstr += '\t%s _%s[%s];\n'%(GAGet(data,'type')[:-2],GAGet(data,'name'),GAGet(data,'size'))
        cstr += '}NvM_Block%s_DataGroupType;\n\n'%(GAGet(block,'name'))
        fp.write(cstr)
    for block in GLGet('EaBlockList'):
        cstr = '\ntypedef struct{\n'
        for data in GLGet(block,'DataList'):
            if( GAGet(data,'type') == 'uint32' or 
                GAGet(data,'type') == 'uint16' or 
                GAGet(data,'type') == 'uint8'):
                cstr += '\t%s _%s;\n'%(GAGet(data,'type'),GAGet(data,'name'))
            else:
                cstr += '\t%s _%s[%s];\n'%(GAGet(data,'type')[:-2],GAGet(data,'name'),GAGet(data,'size'))
        cstr += '}NvM_Block%s_DataGroupType;\n\n'%(GAGet(block,'name'))
        fp.write(cstr)        
    for block in GLGet('FeeBlockList'):
        cstr = '\nextern NvM_Block%s_DataGroupType NvM_Block%s_DataGroup_RAM;\n'%(GAGet(block,'name'),GAGet(block,'name'))
        cstr+= 'extern const NvM_Block%s_DataGroupType NvM_Block%s_DataGroup_ROM;\n'%(GAGet(block,'name'),GAGet(block,'name'))
        fp.write(cstr)
    for block in GLGet('EaBlockList'):
        cstr = '\nextern NvM_Block%s_DataGroupType NvM_Block%s_DataGroup_RAM;\n'%(GAGet(block,'name'),GAGet(block,'name'))
        cstr+= 'extern const NvM_Block%s_DataGroupType NvM_Block%s_DataGroup_ROM;\n'%(GAGet(block,'name'),GAGet(block,'name'))
        fp.write(cstr)        
    fp.write("""
#define Rte_NvMReadBuffer(GroupName)    ((uint8*)&NvM_Block##GroupName##_DataGroup_RAM)    
#define Rte_NvMRead(GroupName,DataName) (NvM_Block##GroupName##_DataGroup_RAM._##DataName)
#define Rte_NvMReadArrayBuffer(GroupName,DataName) ((uint8*)NvM_Block##GroupName##_DataGroup_RAM._##DataName)
#define Rte_NvMReadArray(GroupName,DataName,Index) (NvM_Block##GroupName##_DataGroup_RAM._##DataName[Index])

#define Rte_NvMReadBufferConst(GroupName)    ((uint8*)&NvM_Block##GroupName##_DataGroup_ROM) 
#define Rte_NvMReadConst(GroupName,DataName) (NvM_Block##GroupName##_DataGroup_ROM._##DataName)
#define Rte_NvMReadArrayBufferConst(GroupName,DataName) ((uint8*)NvM_Block##GroupName##_DataGroup_ROM._##DataName)
#define Rte_NvMReadArrayConst(GroupName,DataName,Index) (NvM_Block##GroupName##_DataGroup_ROM._##DataName[Index])

#define Rte_NvMWrite(GroupName,DataName,Value) (NvM_Block##GroupName##_DataGroup_RAM._##DataName = Value)
#define Rte_NvMWriteArray(GroupName,DataName,Index,Value) (NvM_Block##GroupName##_DataGroup_RAM._##DataName[Index] = Value)

#define Rte_NvmWriteBlock(GroupName) NvM_WriteBlock(NVM_BLOCK_ID_##GroupName,(uint8*)&NvM_Block##GroupName##_DataGroup_RAM)
#define Rte_NvmReadBlock(GroupName)  NvM_ReadBlock(NVM_BLOCK_ID_##GroupName,(uint8*)&NvM_Block##GroupName##_DataGroup_RAM)      \n\n""")
    
    fp.write('\n\n#endif /*NVM_CFG_H_*/\n\n')
    fp.close()
    
def GenC():
    global __dir
    fp = open('%s/NvM_Cfg.c'%(__dir),'w')
    fp.write(__Header) 
    fp.write('#include "NvM.h"\n#include "Fee.h"\n#include "Ea.h"\n\n') 
    for block in GLGet('FeeBlockList'):
        cstr = '\nNvM_Block%s_DataGroupType NvM_Block%s_DataGroup_RAM;\n'%(GAGet(block,'name'),GAGet(block,'name'))
        cstr+= 'const NvM_Block%s_DataGroupType NvM_Block%s_DataGroup_ROM={\n'%(GAGet(block,'name'),GAGet(block,'name'))
        for data in GLGet(block,'DataList'):
            if( GAGet(data,'type') == 'uint32' or 
                GAGet(data,'type') == 'uint16' or 
                GAGet(data,'type') == 'uint8'):
                cstr += '\t._%s=%s,\n'%(GAGet(data,'name'),GAGet(data,'default'))
            else:
                cstr += '\t._%s={%s},\n'%(GAGet(data,'name'),GAGet(data,'default'))
        cstr += '};\n\n'
        fp.write(cstr)
    for block in GLGet('EaBlockList'):
        cstr = '\nNvM_Block%s_DataGroupType NvM_Block%s_DataGroup_RAM;\n'%(GAGet(block,'name'),GAGet(block,'name'))
        cstr+= 'const NvM_Block%s_DataGroupType NvM_Block%s_DataGroup_ROM={\n'%(GAGet(block,'name'),GAGet(block,'name'))
        for data in GLGet(block,'DataList'):
            if( GAGet(data,'type') == 'uint32' or 
                GAGet(data,'type') == 'uint16' or 
                GAGet(data,'type') == 'uint8'):
                cstr += '\t._%s=%s,\n'%(GAGet(data,'name'),GAGet(data,'default'))
            else:
                cstr += '\t._%s={%s},\n'%(GAGet(data,'name'),GAGet(data,'default'))
        cstr += '};\n\n'
        fp.write(cstr)        
    cstr = 'const NvM_BlockDescriptorType BlockDescriptorList[] = {\n'
    for block in GLGet('FeeBlockList'):
        cstr += """
    {
        .BlockManagementType = NVM_BLOCK_NATIVE,
        .SelectBlockForReadall = TRUE,
        .SingleBlockCallback = NULL,
        .NvBlockLength        = %s,
        .BlockUseCrc  = TRUE,
        .BlockCRCType =NVM_CRC16,
        .RamBlockDataAddress = (uint8*)&NvM_Block%s_DataGroup_RAM,
        .CalcRamBlockCrc = FALSE, // TODO
        .NvBlockNum = FEE_BLOCK_NUM_%s,
        .NvramDeviceId = FEE_INDEX,
        .NvBlockBaseNumber = FEE_BLOCK_NUM_%s,
        .InitBlockCallback = NULL,
        .RomBlockDataAdress = (uint8*)&NvM_Block%s_DataGroup_ROM,
    },\n"""%(GAGet(block,'BlockSize'),
             GAGet(block,'name'),
             GAGet(block,'name'),
             GAGet(block,'name'),
             GAGet(block,'name'),
             )
    for block in GLGet('EaBlockList'):
        cstr += """
    {
        .BlockManagementType = NVM_BLOCK_NATIVE,
        .SelectBlockForReadall = TRUE,
        .SingleBlockCallback = NULL,
        .NvBlockLength        = %s,
        .BlockUseCrc  = TRUE,
        .BlockCRCType =NVM_CRC16,
        .RamBlockDataAddress = (uint8*)&NvM_Block%s_DataGroup_RAM,
        .CalcRamBlockCrc = FALSE, // TODO
        .NvBlockNum = EA_BLOCK_NUM_%s,
        .NvramDeviceId = EA_INDEX,
        .NvBlockBaseNumber = EA_BLOCK_NUM_%s,
        .InitBlockCallback = NULL,
        .RomBlockDataAdress = (uint8*)&NvM_Block%s_DataGroup_ROM,
    },\n"""%(GAGet(block,'BlockSize'),
             GAGet(block,'name'),
             GAGet(block,'name'),
             GAGet(block,'name'),
             GAGet(block,'name'),
             )    
    cstr += """};

const NvM_ConfigType NvM_Config = {
    .Common = {
        .MultiBlockCallback = NULL,
    },
    .BlockDescriptor = BlockDescriptorList,        
};\n\n"""
    fp.write(cstr) 
    fp.close()
