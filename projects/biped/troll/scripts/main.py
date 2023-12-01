import importlib
import maya.cmds as cmds
from projects.biped.troll.scripts import build
from modules.nodel import Dag_Node as Dag, Joint, Curve
from modules.utils import tools

importlib.reload(tools)
importlib.reload(build)
# ---------------------------------------------------------------------------------------------
# build scene
# ---------------------------------------------------------------------------------------------
scene = build.setup('biped', 'troll')
buildGrp = Dag("build_objects_grp")

# ---------------------------------------------------------------------------------------------
# create base groups
# ---------------------------------------------------------------------------------------------
baseGroupData = scene.createBaseGroups()
topGrp = baseGroupData['topGrp']
jointGrp = baseGroupData['jointGrp']
modelGrp = baseGroupData['modelGrp']
controlsGrp = baseGroupData['controlsGrp']

# ---------------------------------------------------------------------------------------------
# re-parent groups
# ---------------------------------------------------------------------------------------------
assetModelGrp = Dag("troll_proxy_grp")
assetModelGrp.parentTo(modelGrp)
rootJnt = Joint("root1_jnt")
rootJnt.parentTo(jointGrp)

# ---------------------------------------------------------------------------------------------
# set global control
# ---------------------------------------------------------------------------------------------
globalControl_dict = scene.createGlobalControl(rigScale=5, shape="sun")
globalControl = globalControl_dict['c']
globalControl_offset = globalControl_dict['off']
globalControl_offset.parentTo(topGrp)
for c in ['t', 'r', 's']:
    globalControl.a[c] >> jointGrp.a[c]
    globalControl.a[c] >> controlsGrp.a[c]

# ---------------------------------------------------------------------------------------------
# create setting control
# ---------------------------------------------------------------------------------------------
refObj = "head1_jnt"
settingCtrl_dict = scene.createSettingControl(prefix="setting", refObj=refObj, parentObj=globalControl,
                                              offsetValue=20, rigScale=5)
settingCtrl = settingCtrl_dict["c"]
settingCtrlOffset = settingCtrl_dict["off"]
Joint(refObj).parentConstraint(settingCtrlOffset, mo=1)

# ---------------------------------------------------------------------------------------------
# add setting control's attribute
# ---------------------------------------------------------------------------------------------
visAttr = ['jointsVis', 'modelVis', "controlsVis"]
displayAttr = ["jointsDisType", "modelDisType", "controlsDisType"]
mainGroups = [jointGrp, modelGrp, controlsGrp]

for grp, visAt, disAt in zip(mainGroups, visAttr, displayAttr):
    settingCtrl.a.add(ln=visAt, at='enum', enumName='off:on', k=True, dv=1)
    settingCtrl.a[visAt] >> grp.a.v
    if grp == jointGrp:
        settingCtrl.a[visAt].set(0)

    if not grp == controlsGrp:
        settingCtrl.a.add(ln=disAt, at='enum', enumName='normal:template:reference', k=True, dv=2)
        grp.a['ove'].set(1)
        settingCtrl.a[disAt] >> grp.a['ovdt']

# ---------------------------------------------------------------------------------------------
# build control setup
# ---------------------------------------------------------------------------------------------
# rig spine
spineJoints = [Joint(i) for i in cmds.ls("*spine*", type='joint')]
spineData = scene.rig_spine(ribbonSurface='spine_ribbon_srf', spineJoints=spineJoints,
                            pelvisJnt='pelvis1_jnt', rootJnt=rootJnt, rigScale=5)
spine_mGrp = spineData["mainGrp"]
spine_mGrp.parentTo(controlsGrp)

# rig head
neckJointsList = ['neck1_jnt', 'neck2_jnt', 'neck3_jnt', 'neck4_jnt']
mouthRootJointList = ['mouth_lower_middle_root_jnt', 'l_mouth_lower_corner_root_jnt', 'r_mouth_lower_corner_root_jnt',
                      'r_mouth_lower_outer_root_jnt', 'l_mouth_lower_outer_root_jnt', 'r_mouth_upper_corner_root_jnt',
                      'l_mouth_upper_corner_root_jnt', 'mouth_upper_middle_root_jnt', 'l_mouth_upper_outer_root_jnt',
                      'r_mouth_upper_outer_root_jnt']
eyelidJntList = ['l_eyeLidUp1_jnt', 'l_eyeLidDown1_jnt', 'r_eyeLidUp1_jnt', 'r_eyeLidDown1_jnt', 'l_ear1_jnt',
                 'r_ear1_jnt']
headData = scene.rig_head(neckJoints=neckJointsList, headJoint='head1_jnt', lEyeJnt='l_eye1_jnt', rEyeJnt='r_eye1_jnt',
                          jawJnt='jaw1_jnt', mouthJnt=mouthRootJointList, noseJnt='nose1_jnt', eyeAim_loc='eyeAim_loc',
                          eyelidEarJnt=eyelidJntList, rigScale=5)
headData['mainGrp'].parentTo(controlsGrp)
spineJoints[-2].parentConstraint(headData['baseGrp'], mo=1)
spineData['bodyCtrl']['c'].parentConstraint(headData['headOrientGrp'], mo=1)

# rig arm
for side in ['l', 'r']:
    armData = scene.rig_limbs(startJoint=side + '_shoulder1_jnt', midJoint=side + '_elbow1_jnt',
                              endJoint=side + '_hand1_jnt', clavicleJnt=side + '_clavicle1_jnt',
                              pvRefObj=side + '_armPoleVec_loc', ikCtrlRefObj=side + '_hand_loc',
                              scapulaJnt=side + '_scapula1_jnt',
                              prefix=side + '_arm_', partType='arm', rigScale=5)
    armData['mainGrp'].parentTo(controlsGrp)
    Joint('spine5_jnt').parentConstraint(armData['baseGrp'], mo=1)
    spineData['bodyCtrl']['c'].parentConstraint(armData['ikBaseGrp'], mo=1)

# rig leg
for side in ['l', 'r']:
    revJnts = [side + '_heel1_rev_jnt', side + '_toes1_rev_jnt', side + '_ball1_rev_jnt', side + '_foot1_rev_jnt']
    legData = scene.rig_limbs(startJoint=side + '_hip1_jnt', midJoint=side + '_knee1_jnt',
                              endJoint=side + '_foot1_jnt',
                              pvRefObj=side + '_legPoleVec_loc', revJnts=revJnts,
                              bankRefLoc=[side + '_inverse_loc', side + '_outverse_loc'],
                              ikCtrlRefObj=side + '_footMiddle_loc', toeJnt=side + '_toes1_jnt',
                              prefix=side + '_leg_', partType='leg', rigScale=5)
    legData['mainGrp'].parentTo(controlsGrp)
    Joint('pelvis1_jnt').parentConstraint(legData['baseGrp'], mo=1)
# ---------------------------------------------------------------------------------------------
# load skin model weights
# ---------------------------------------------------------------------------------------------
scene.loadSkinWeights(modelGrp)

# ---------------------------------------------------------------------------------------------
# apply tension deformer
# ---------------------------------------------------------------------------------------------
bodyTensionDf = Dag(cmds.tension('body_geo', inwardConstraint=1)[0])
bodyTensionDf.a['squashConstraint', 0]

# # ---------------------------------------------------------------------------------------------
# # correctives
# # ---------------------------------------------------------------------------------------------
headData['correctivesGrp'].parentTo(topGrp)

# ---------------------------------------------------------------------------------------------
# wrap high resolution model
# ---------------------------------------------------------------------------------------------
scene.hiresWrapModel(baseGroupData)

# ---------------------------------------------------------------------------------------------
# delete initial group
# ---------------------------------------------------------------------------------------------
buildGrp.delete()

# ---------------------------------------------------------------------------------------------
# set color
# ---------------------------------------------------------------------------------------------
controls = [Curve(i).parent for i in cmds.ls(typ='nurbsCurve')]
[crv.setColour(22) for crv in controls]
[crv.setColour(13) for crv in controls if crv.name.startswith('l_') or '_l_' in crv.name]
[crv.setColour(6) for crv in controls if crv.name.startswith('r_') or '_r_' in crv.name]
