"""
Author:SuoLin Zhang
Created:2023
About: All functions to build to a simple biped rig
"""
import maya.cmds as cmds
import maya.mel as mel
from modules.nodel import Dag_Node as Dag, Curve, Mesh, Joint, Dep_Node as Dep
from modules.controller_lib import Controller
from modules.utils import tools


class setup(object):
    def __init__(self, typeName='', charName=''):
        self.charName = charName
        self.type = typeName

        self.projectPath = r"C:\Coding\rigging_tools\Projects\%s\%s/"

        self.modelPath = '%smod/%s_proxy_model.ma'

        self.skeletonPath = '%sskeleton/%s_skeleton.ma'

        self.hiresModelPath = '%smod/%s_model.ma'

        self.faceShapesPath = "%smod/%s_proxy_faceshapes.ma"

        self.mainProjectPath = self.projectPath % (self.type, self.charName)

        self.createScene()

    def createScene(self):
        """
        create the scene and import all needed files
        """

        modelPathFile = self.modelPath % (self.mainProjectPath, self.charName)

        skeletonPathFile = self.skeletonPath % (self.mainProjectPath, self.charName)

        hiresModelPathFile = self.hiresModelPath % (self.mainProjectPath, self.charName)

        cmds.file(new=True, force=True)

        # import model
        cmds.file(modelPathFile, i=True)

        # import skeleton
        cmds.file(skeletonPathFile, i=True)

        # import high resolution model
        cmds.file(hiresModelPathFile, i=True)

        cmds.viewFit()

    def createGroup(self, *args, **kwargs):
        """function to create group and convert it to Dag node"""
        return Dag(cmds.group(*args, **kwargs))

    def createBaseGroups(self,
                         topGrpName='_rig_grp',
                         jointGrpName="joints_grp",
                         modelGrpName="model_grp",
                         controlsGrpName="controls_grp",
                         ):
        """
        create base groups to sort all objects in our rig
        Args:
            topGrpName(str): name of top group, default: '_rig_grp'.
            jointGrpName(str): name of joint group, default: "joints_grp".
            modelGrpName(str): name of model group, default: "model_grp".
            controlsGrpName(str): name of controls group, default: "controls_grp".

        Returns:
            {
            'topGrp': topGrp,
            'jointGrp': jointGrp,
            'modelGrp': modelGrp,
            'controlsGrp': controlsGrp,
            }
        """

        topGrp = self.createGroup(n=self.charName + topGrpName, em=True)
        jointGrp = self.createGroup(n=jointGrpName, em=True, p=topGrp)
        modelGrp = self.createGroup(n=modelGrpName, em=True, p=topGrp)
        controlsGrp = self.createGroup(n=controlsGrpName, em=True, p=topGrp)

        # lock attribute of top group
        for attr in ['t', 'r', 's']:
            for axis in ['x', 'y', 'z']:
                topGrp.a[attr + axis].set(l=True, keyable=False, channelBox=False)

        return {'topGrp': topGrp,
                'jointGrp': jointGrp,
                'modelGrp': modelGrp,
                'controlsGrp': controlsGrp,
                }

    def createGlobalControl(self, prefix='global', rigScale=1.0, shape="sun", **kwargs):
        """
        function to create global control
        Args:
            prefix(str): prefix of global control name
            rigScale(float): value to adjust global control size, default: 1,0.
            shape(str): shape of global control, default: "sun".(
                                                                "ctrlCircle",
                                                                "io",
                                                                "pyramid",
                                                                "pyramidUp"
                                                                "twoArrows",
                                                                "normalArrow",
                                                                "fatArrow",
                                                                "crossCircle",
                                                                "disc",
                                                                "waveCircle",
                                                                "rightEye",
                                                                "leftEye",
                                                                "rightFoot",
                                                                "leftFoot",
                                                                "sun",
                                                                "create"
                                                                )
        Returns:
            {
            'c': globalCtrl,
            'off': globalCtrlOffset
            }

        """
        # create global control
        globalCtrl = Curve(Controller(prefix=prefix, ctrlShape=shape, size=rigScale * 30, **kwargs).node)
        globalCtrlOffset = globalCtrl.createOffset()
        return {
            'c': globalCtrl,
            'off': globalCtrlOffset
        }

    def createSettingControl(self, prefix, refObj, parentObj, offsetValue, rigScale=1.0, shape="pyramidUp", **kwargs):
        """
        function to create setting control
        Args:
            prefix(str): prefix of global control name
            rigScale(float): value to adjust control size
            refObj(object): object to match move
            parentObj(object): object to parent to
            offsetValue(float): value to move away from head
            shape(str): shape to create, default: "pyramidUp".(
                                                            "ctrlCircle",
                                                            "io",
                                                            "pyramid",
                                                            "pyramid",
                                                            "twoArrows",
                                                            "normalArrow",
                                                            "fatArrow",
                                                            "crossCircle",
                                                            "disc",
                                                            "waveCircle",
                                                            "rightEye",
                                                            "leftEye",
                                                            "rightFoot",
                                                            "leftFoot",
                                                            "sun",
                                                            "create"
                                                            )
        Returns:
            {
            'c': globalCtrl,
            'off': globalCtrlOffset
            }
        """
        refObj = Dag(refObj)
        settingControl = Curve(Controller(prefix, size=rigScale, ctrlShape=shape, **kwargs).node)
        offset = settingControl.createOffset()
        offset.moveTo(refObj, point=True)
        offset.a.ty.set(offset.a.ty.get() + offsetValue + rigScale * 2)
        offset.parentTo(parentObj)

        return {
            'c': settingControl,
            'off': offset
        }

    def createNewModule(self, prefix):
        """create a new module to contain all objects of a rigging setup"""
        mainGrp = self.createGroup(n=prefix + 'RigModule_grp', em=True)
        controlsGrp = self.createGroup(n=prefix + 'Controls_grp', p=mainGrp, em=True)
        partsGrp = self.createGroup(n=prefix + 'Parts_grp', p=mainGrp, em=True)
        partsStaticGrp = self.createGroup(n=prefix + 'PartsStatic_grp', p=mainGrp, em=True)

        cmds.hide(partsGrp, partsStaticGrp)
        partsStaticGrp.a['it'].set(0)
        return {
            'mainGrp': mainGrp,
            'controlsGrp': controlsGrp,
            'partsGrp': partsGrp,
            'partsStaticGrp': partsStaticGrp
        }

    def createControl(self, prefix, controlScale, ctrlShape, matchMoveObj, parentObj,
                      point=False, orient=False, **kwargs):
        """
        a common function to create all controls of the rig
        Args:
            prefix(str): prefix of global control name
            controlScale(float): value to adjust control size
            matchMoveObj(object): object to match move
            parentObj(object): object to parent to
            point: move constraint type
            ctrlShape(str): shape to create, default: "pyramidUp".(
                                                            "ctrlCircle",
                                                            "io",
                                                            "spike",
                                                            "pyramid",
                                                            "pyramidUp",
                                                            "twoArrows",
                                                            "normalArrow",
                                                            "fatArrow",
                                                            "crossCircle",
                                                            "disc",
                                                            "waveCircle",
                                                            "rightEye",
                                                            "leftEye",
                                                            "rightFoot",
                                                            "leftFoot",
                                                            "sun",
                                                            "create"
                                                            )
        Returns:
            {
            'c': globalCtrl,
            'off': globalCtrlOffset
            }
        """
        ctrl = Curve(Controller(prefix=prefix, ctrlShape=ctrlShape, size=controlScale, **kwargs).node)
        ctrlOff = ctrl.createOffset()
        if point or orient:
            if point:
                ctrlOff.moveTo(matchMoveObj, point=True)
            if orient:
                ctrlOff.moveTo(matchMoveObj, orient=True)
        else:
            ctrlOff.moveTo(matchMoveObj)

        if parentObj:
            ctrlOff.parentTo(parentObj)

        return {
            'c': ctrl,
            'off': ctrlOff
        }

    def rig_spine(self, ribbonSurface, spineJoints, pelvisJnt, rootJnt, prefix='spine_', rigScale=1.0):
        """spine rigging setup
        Args:
            ribbonSurface(str): name
            spineJoints(str): name
            prefix(str): 'spine_'
            rootJnt(str): name
            pelvisJnt(str): name
            rigScale(float): distance or scale reference
        Returns:
            {
            'mainGrp': mainGrp,
            'controlsGrp': controlsGrp,
            'moduleObjs': moduleObjs,
            'bodyCtrl': bodyCtrl
            }
        """
        # make new module
        moduleObjs = self.createNewModule(prefix)
        mainGrp = moduleObjs['mainGrp']
        controlsGrp = moduleObjs['controlsGrp']
        partsGrp = moduleObjs['partsGrp']
        partsStaticGrp = moduleObjs['partsStaticGrp']

        # make controls
        bodyCtrl = self.createControl(prefix=prefix + 'Body', controlScale=rigScale * 25, ctrlShape='waveCircle',
                                      matchMoveObj=rootJnt, point=True, parentObj=controlsGrp)
        pelvisJnt = Dag(pelvisJnt)
        pelvisJntEnd = pelvisJnt.children[0]
        hipsControl = self.createControl(prefix=prefix + 'Hips', controlScale=rigScale * 13, ctrlShape='ctrlCircle',
                                         nr=(0, 1, 0), matchMoveObj=pelvisJnt, point=True, parentObj=bodyCtrl['c'])
        hipsLocalControl = self.createControl(prefix=prefix + 'HipsLocal', controlScale=rigScale * 11,
                                              ctrlShape='ctrlCircle', nr=(0, 1, 0),
                                              matchMoveObj=pelvisJnt, point=True, parentObj=hipsControl['c'])
        chestControl = self.createControl(prefix=prefix + 'Chest', controlScale=rigScale * 18, ctrlShape='disc',
                                          matchMoveObj=spineJoints[-3], point=True, parentObj=bodyCtrl['c'])
        chestLocalControl = self.createControl(prefix=prefix + 'ChestLocal', controlScale=rigScale * 18,
                                               ctrlShape='disc',
                                               matchMoveObj=spineJoints[-2], point=True, parentObj=chestControl['c'])

        # offset hips control
        hipsClus, hipsClusHdl = cmds.cluster(hipsControl['c'], n='tempShapeOffset_clus')
        cmds.delete(cmds.pointConstraint(pelvisJnt, pelvisJntEnd, hipsClusHdl))
        hipsControl['c'].deleteHistory()

        bodyCtrl['c'].parentConstraint(rootJnt, mo=True)

        hipsLocalControl['c'].parentConstraint(pelvisJnt, mo=True)
        chestLocalControl['c'].parentConstraint(spineJoints[-2], mo=True)

        # ribbon setup
        ribbon = Curve(ribbonSurface)
        ribbon.parentTo(partsStaticGrp)
        ribbonFollicleGrp = Dag(cmds.group(n=prefix + 'RibbonFolic_grp', em=True, p=partsStaticGrp))
        closestPointNode = Dep(prefix + 'ClosestRibbonPoint_cpo', nodeType='closestPointOnSurface')
        ribbon.shape.a['ws'] >> closestPointNode.a['is']

        for num, spineJnt in enumerate(spineJoints[:-2]):
            jntPos = Joint(spineJnt).o.position[0:3]
            closestPointNode.a['inPosition'].set(jntPos[0], jntPos[1], jntPos[2])
            uParam = closestPointNode.a['parameterU'].get()
            vParam = closestPointNode.a['parameterV'].get()

            folic = Dag(cmds.createNode('follicle', n='%sRibbon%s_folShape' % (prefix, num + 1)))
            folic.a['sim'].set(0)
            folicTrans = folic.parent
            folicTrans.parentTo(ribbonFollicleGrp)
            ribbon.a['worldMatrix'] >> folic.a['inputWorldMatrix']
            ribbon.shape.a['local'] >> folic.a['inputSurface']

            folic.a['outTranslate'] >> folicTrans.a['t']
            folic.a['outRotate'] >> folicTrans.a['r']

            folic.a['parameterU'].set(uParam)
            folic.a['parameterV'].set(vParam)
            folicTrans.parentConstraint(spineJnt, mo=True)

        closestPointNode.delete()

        # connect controls to ribbon surface
        chestRibbonCvs = '%s.cv[0:3][0:1]' % ribbonSurface
        hipsRibbonCvs = '%s.cv[0:3][2:3]' % ribbonSurface

        chestRibbonClsHdl = cmds.cluster(chestRibbonCvs, wn=[chestControl['c'], chestControl['c']], bs=1,
                                         n=prefix + 'ChestRibbon_clus')[0]
        hipsRibbonClsHdl = \
            cmds.cluster(hipsRibbonCvs, wn=[hipsControl['c'], hipsControl['c']], bs=1, n=prefix + 'HipsRibbon_clus')[0]
        cmds.sets([chestRibbonClsHdl, hipsRibbonClsHdl], n='ribbonCluster')
        return {
            'mainGrp': mainGrp,
            'controlsGrp': controlsGrp,
            'moduleObjs': moduleObjs,
            'bodyCtrl': bodyCtrl
        }

    def rig_head(self, neckJoints, headJoint, eyeAim_loc, lEyeJnt, rEyeJnt, jawJnt, mouthJnt, noseJnt, eyelidEarJnt,
                 ikCurve='neck_crv', prefix='head_', rigScale=1.0):
        """head rigging setup
        Args:
            neckJoints(str): name
            headJoint(str): name
            eyeAim_loc(str): name of eye aim locator
            ikCurve(str): name of ik spline reference curve
            eyelidEarJnt(str): name
            noseJnt(str): name
            mouthJnt(str): name
            jawJnt(str): name
            rEyeJnt(str): name
            lEyeJnt(str): name
            prefix(str): 'head_'
            rigScale(float): distance or scale reference

        Returns:
            {
            'mainGrp': mainGrp,
            'moduleObjs': moduleObjs,
            'baseGrp': neckBaseGrp,
            'headOrientGrp': headOrientGrp,
            'correctivesGrp': correctivesGrp
            }
            """
        # make new module
        moduleObjs = self.createNewModule(prefix)
        mainGrp = moduleObjs['mainGrp']
        controlsGrp = moduleObjs['controlsGrp']
        partsGrp = moduleObjs['partsGrp']
        partsStaticGrp = moduleObjs['partsStaticGrp']
        neckBaseGrp = self.createGroup(em=True, n=prefix + 'NeckBase_grp', p=partsGrp)  # substantial group
        headOrientGrp = self.createGroup(n=prefix + 'Orient_Grp', em=True, p=neckBaseGrp)

        # head setup
        headCtrl = self.createControl(prefix=prefix + 'Main', controlScale=rigScale * 5, ctrlShape='ctrlCircle',
                                      nr=(0, 1, 0),
                                      matchMoveObj=headJoint, point=True, parentObj=controlsGrp)
        headEndJnt = Joint(headJoint).children[0]
        headClus, headClusHdl = cmds.cluster(headCtrl['c'], n='tempShapeOffset_clus')
        cmds.delete(cmds.pointConstraint(headEndJnt, headClusHdl))
        headCtrl['c'].deleteHistory()

        headOrientGrp.orientConstraint(headCtrl['off'], mo=1)
        neckBaseGrp.parentConstraint(headCtrl['c'], sr=['x', 'y', 'z'], mo=1)
        headCtrl['c'].orientConstraint(headJoint, mo=True)

        # neck twist
        neckIkChain = Dag(cmds.ikHandle(n=prefix + 'Neck_ik', sol='ikSplineSolver', sj=neckJoints[0], ee=neckJoints[-1],
                                        c=ikCurve, ccv=0, parentCurve=0)[0])
        cmds.parent(neckIkChain, ikCurve, partsStaticGrp)

        neckTwistGrp = self.createGroup(em=True, n=prefix + 'NeckTwist_grp', p=partsGrp)
        neckTwistOffsetGrp = neckTwistGrp.createOffset()
        neckTwistOffsetGrp.moveTo(neckJoints[0], point=True)
        neckTwistOffsetGrp.parentTo(neckBaseGrp)

        headCtrl['c'].aimConstraint(neckTwistOffsetGrp, aim=[1, 0, 0], u=[0, 0, 1], wut='objectrotation',
                                    wu=[1, 0, 0], wuo=neckBaseGrp)
        neckTwistOriConstr = headCtrl['c'].parentConstraint(neckTwistGrp, mo=1, st=['x', 'y', 'z'])
        neckTwistOriConstr.a['interpType'].set(2)
        neckTwistGrp.a.rx >> neckIkChain.a['twist']

        cmds.cluster(ikCurve + '.cv[0:1]', wn=(neckBaseGrp, neckBaseGrp), bs=True)
        cmds.cluster(ikCurve + '.cv[2:3]', wn=(headCtrl['c'], headCtrl['c']), bs=True)

        # jaw
        jawEndJnt = Joint(jawJnt).children[0]
        jawCtrl = self.createControl(prefix=prefix + 'Jaw', ctrlShape='ctrlCircle', nr=(0, 1, 0),
                                     controlScale=rigScale * 2,
                                     matchMoveObj=jawJnt, parentObj=headCtrl['c'])
        jawClus, jawClusHdl = cmds.cluster(jawCtrl['c'], n='tempShapeOffset_cls')
        Dag(jawClusHdl).moveTo(jawEndJnt, point=True)
        Dag(jawClusHdl).move(0, -rigScale, 0, r=True)
        jawCtrl['c'].deleteHistory()
        jawCtrl['c'].parentConstraint(jawJnt, mo=1)

        # -----------------------------------------------------------------------------------------------------------
        # basic face setup #
        # -----------------------------------------------------------------------------------------------------------
        # tongue setup
        topTongueJnt = Joint('tongue1_jnt')
        chainJoints = topTongueJnt.allChildren[1:]
        chainJoints.append(topTongueJnt)
        chainJoints.reverse()

        chainControls = []

        for i, joint in enumerate(chainJoints):
            ctrlPrefix = 'tongue%d' % (i + 1)
            ctrlParent = 'controls_grp'
            if i > 0:

                ctrlParent = chainControls[i - 1]['c']

            ctrl = self.createControl(prefix=prefix + ctrlPrefix, controlScale=rigScale, ctrlShape='ctrlCircle', nr=(1, 0, 0),
                                      matchMoveObj=joint, parentObj=ctrlParent)
            ctrlCls, ctrlClsHdl = cmds.cluster(ctrl['c'], n='tempShapeOffset_cls')
            cmds.delete(cmds.pointConstraint(joint, joint.children[0], ctrlClsHdl))
            ctrl['c'].deleteHistory()

            if ctrlParent != 'controls_grp':
                ctrlParent.parentConstraint(ctrl['off'], mo=1)

            ctrl['c'].parentConstraint(joint, mo=1)

            chainControls.append(ctrl)

        Joint(jawJnt).parentConstraint(chainControls[0]['off'], mo=1)

        # eyes
        eyesCtrl = self.createControl(prefix=prefix + 'EyeAim', controlScale=rigScale, ctrlShape='ctrlCircle',
                                      matchMoveObj=eyeAim_loc, parentObj=controlsGrp, point=True)
        headCtrl['c'].parentConstraint(eyesCtrl['off'], mo=1)
        middleEyesAimGrp = Dag(self.createGroup(em=True, n=prefix + 'middleEyesAimGrp', p=partsGrp))
        cmds.delete(cmds.pointConstraint(lEyeJnt, rEyeJnt, middleEyesAimGrp))
        eyesCtrl['c'].aimConstraint(middleEyesAimGrp, aim=[1, 0, 0], u=[0, 1, 0], wu=[1, 0, 0], wut='objectrotation',
                                    wuo=headJoint)
        for eyeJoint in [lEyeJnt, rEyeJnt]:
            middleEyesAimGrp.orientConstraint(eyeJoint, mo=True)

        # eyebrow
        leftBrowCtrl = self.createControl(prefix=prefix + 'l_brow', controlScale=rigScale, ctrlShape='spike',
                                          matchMoveObj='l_brow_middle_jnt', parentObj=headCtrl['c'])
        rightBrowCtrl = self.createControl(prefix=prefix + 'r_brow', controlScale=rigScale, ctrlShape='spike',
                                           matchMoveObj='r_brow_middle_jnt', parentObj=headCtrl['c'])
        leftBrowCtrl['c'].clsMove(1.5, y=1, r=1)
        leftBrowCtrl['c'].clsRotate(90, y=1, r=1)
        rightBrowCtrl['c'].clsMove(1.5, y=1, r=1)
        rightBrowCtrl['c'].clsRotate(90, y=1, r=1)

        browJnt = cmds.ls("*brow*", typ='joint')
        for jnt in browJnt:
            if 'l_' in jnt:
                ctrl = self.createControl(prefix=prefix + jnt[:-4], controlScale=rigScale * 0.2,
                                          ctrlShape='ctrlCircle',
                                          nr=(1, 0, 0), matchMoveObj=jnt, parentObj=leftBrowCtrl['c'])
            elif 'r_' in jnt:
                ctrl = self.createControl(prefix=prefix + jnt[:-4], controlScale=rigScale * 0.2,
                                          ctrlShape='ctrlCircle',
                                          nr=(1, 0, 0), matchMoveObj=jnt, parentObj=rightBrowCtrl['c'])
            else:
                ctrl = self.createControl(prefix=prefix + jnt[:-4], controlScale=rigScale * 0.2,
                                          ctrlShape='ctrlCircle',
                                          nr=(1, 0, 0), matchMoveObj=jnt, parentObj=headCtrl['c'])
            ctrl['off'].move(0.8, 0, 0, r=1, os=1, wd=1)
            ctrl['c'].o.copyPivotFrom(jnt)
            ctrl['c'].parentConstraint(jnt, mo=1)

        # eyelid and ear
        for jnt in eyelidEarJnt:
            endJnt = Joint(jnt).children[0]
            ctrl = self.createControl(prefix=prefix + jnt[:-4], controlScale=rigScale * 0.6,
                                      ctrlShape='ctrlCircle',
                                      nr=(0, 1, 0), matchMoveObj=jnt, parentObj=headCtrl['c'])
            Cls, ClsHdl = cmds.cluster(ctrl['c'])
            Dag(ClsHdl).moveTo(endJnt, point=1)
            ctrl['c'].deleteHistory()
            ctrl['c'].parentConstraint(jnt, mo=1)

        # cheek, sneer and squint
        joints = cmds.ls('*cheek*', typ='joint')
        joints.extend(cmds.ls('*sneer*'))
        joints.extend(cmds.ls('*squze*'))
        for jnt in joints:
            ctrl = self.createControl(prefix=prefix + jnt[:-4], controlScale=rigScale * 0.2,
                                      ctrlShape='ctrlCircle',
                                      nr=(1, 0, 0), matchMoveObj=jnt, parentObj=headCtrl['c'])
            ctrl['off'].move(1, 0, 0, r=1, os=1, wd=1)
            ctrl['c'].o.copyPivotFrom(jnt)
            ctrl['c'].parentConstraint(jnt, mo=1)

        # mouth
        mouth_globalCtrl = self.createControl(prefix=prefix + 'mouth', controlScale=rigScale * 1, ctrlShape='fatArrow',
                                              matchMoveObj="mouthAim_loc", parentObj=headCtrl['c'], point=True)
        mouth_globalCtrl['c'].clsRotate(90, x=1)
        lowerMouthGrp = self.createGroup(empty=True, n=prefix + "lower_mouth_OFF_GRP", p=mouth_globalCtrl['c'])
        lowerMouthGrp.moveTo(jawCtrl['c'])
        jawCtrl['c'].orientConstraint(lowerMouthGrp)
        for jnt in mouthJnt:
            rootJnt = Joint(jnt)
            lipJnt = rootJnt.children[0]
            name = lipJnt.name[:-4]
            if 'low' in name:
                ctrl = self.createControl(prefix=prefix + name, controlScale=rigScale * 0.18, ctrlShape='ctrlCircle',
                                          matchMoveObj=lipJnt, parentObj=lowerMouthGrp, point=True)
            else:
                ctrl = self.createControl(prefix=prefix + name, controlScale=rigScale * 0.18, ctrlShape='ctrlCircle',
                                          matchMoveObj=lipJnt, parentObj=mouth_globalCtrl['c'], point=True)
            ctrl['c'].clsMove(0, 0, 1, r=1)
            tools.lips_shape(control=ctrl['c'].node, rootJoint=jnt, headCtrl=headCtrl['c'], jawCtrl=jawCtrl['c'],
                             primAxis='x', secAxis='z')

        # nose
        noseEndJnt = Joint(noseJnt).children[0]
        noseCtrl = self.createControl(prefix=prefix + 'nose', controlScale=rigScale * 1, ctrlShape='ctrlCircle',
                                      nr=(0, 1, 0), matchMoveObj=noseEndJnt, parentObj=headCtrl['c'])
        noseCtrl['c'].parentConstraint(noseJnt)

        # ------------------
        # blendShapes setup
        # ------------------

        # import
        faceShapesPathFile = self.faceShapesPath % (self.mainProjectPath, self.charName)
        cmds.file(faceShapesPathFile, i=1)

        # setup face shapes
        faceShapesGeo = Mesh('faceShapes_geo')
        bodyGeo = Mesh('body_geo')
        faceShapesGeo.parentTo(partsStaticGrp)
        bodyMainBls = cmds.blendShape(faceShapesGeo, bodyGeo, n='bodyMain_bls', w=[0, 1])[0]
        faceBls = faceShapesGeo.blendShapes[0]
        targetIndices = faceBls.a['weight'].get(mi=1)
        bsShapeNames = [cmds.aliasAttr('%s.weight[%d]' % (faceBls, i), q=1) for i in targetIndices]

        faceAt = 'faceShapes'
        headCtrl['c'].a.add(ln=faceAt, at='enum', enumName='-----------', k=0)
        headCtrl['c'].a['faceShapes'].set(cb=1, l=1)

        # correctives
        correctivesGrp = Dag('correctives_grp')
        correctivesGrp.hide()

        # mouth narrow
        targetIdxCount = 1
        mouthNarrowGeo = 'mouthNarrow'
        cmds.blendShape(bodyMainBls, e=1, t=[bodyGeo, targetIdxCount, mouthNarrowGeo, 1.0])
        cmds.setDrivenKeyframe(bodyMainBls+'.'+mouthNarrowGeo, currentDriver=Joint(jawJnt).a.rz, driverValue=0, value=0)
        cmds.setDrivenKeyframe(bodyMainBls + '.' + mouthNarrowGeo, currentDriver=Joint(jawJnt).a.rz, driverValue=-25, value=1)

        for num, shape in zip(targetIndices, bsShapeNames):
            headCtrl['c'].a.add(ln=shape, k=1, min=-1, max=1)
            headCtrl['c'].a[shape] >> faceBls.a['weight[%s]' % num]

        return {
            'mainGrp': mainGrp,
            'moduleObjs': moduleObjs,
            'baseGrp': neckBaseGrp,
            'headOrientGrp': headOrientGrp,
            'correctivesGrp': correctivesGrp
        }

    def rig_limbs(self, startJoint, midJoint, endJoint,
                  pvRefObj=None,
                  ikCtrlRefObj=None,
                  clavicleJnt=None,
                  scapulaJnt=None,
                  toeJnt=None,
                  revJnts=None,
                  bankRefLoc=None,
                  addStretch=True,
                  makeTwistJoints=True,
                  prefix='arm_', partType='arm', rigScale=1.0):
        """arms and legs rigging setup
        Args:
            startJoint(str): name
            midJoint(str): name
            endJoint(str): name
            pvRefObj(str): name of pole vector reference object
            ikCtrlRefObj(str): name of your ik control reference object
            clavicleJnt(str): name
            scapulaJnt(str): name
            toeJnt(str): name
            revJnts(str): name of first reverse foot joint
            bankRefLoc(str): name of bank rotate reference object
            addStretch(bool): default True
            makeTwistJoints(bool): default True
            prefix(str): 'arm_'
            partType(str): 'arm' or 'leg'
            rigScale(float):

        Returns:
            {
            'mainGrp': mainGrp,
            'moduleObjs': moduleObjs,
            'baseGrp': baseGrp,
            'ikBaseGrp': ikBaseGrp
            }

        """
        # make new module
        moduleObjs = self.createNewModule(prefix=prefix)
        mainGrp = moduleObjs['mainGrp']
        controlsGrp = moduleObjs['controlsGrp']
        partsGrp = moduleObjs['partsGrp']
        partsStaticGrp = moduleObjs['partsStaticGrp']
        baseGrp = self.createGroup(n=prefix + 'Base_grp', em=1, p=partsGrp)
        ikBaseGrp = self.createGroup(n=prefix + 'IkBase_grp', em=1, p=partsGrp)

        # make IK controls
        pvCtrl = self.createControl(prefix=prefix + 'Pv', controlScale=rigScale * 3, ctrlShape="pyramid",
                                    matchMoveObj=pvRefObj, parentObj=controlsGrp)
        if partType == 'arm':
            mainIkCtrl = self.createControl(prefix=prefix + 'main', controlScale=rigScale * 10, ctrlShape="normalArrow",
                                            matchMoveObj=ikCtrlRefObj, parentObj=controlsGrp)
        else:
            if prefix.startswith('l_'):
                mainIkCtrl = self.createControl(prefix=prefix + 'foot', controlScale=rigScale * 30,
                                                ctrlShape="leftFoot",
                                                matchMoveObj=ikCtrlRefObj, parentObj=controlsGrp)
                mainIkCtrl['c'].clsMove(-2, 0, 6, r=1)
            else:
                mainIkCtrl = self.createControl(prefix=prefix + 'foot', controlScale=rigScale * 30,
                                                ctrlShape="rightFoot",
                                                matchMoveObj=ikCtrlRefObj, parentObj=controlsGrp)
                mainIkCtrl['c'].clsMove(2, 0, 6, r=1)
            mainIkCtrl['c'].o.copyPivotFrom(endJoint)
            pvCtrl['c'].clsRotate(180, y=1, r=1)

        # Switch ikFK Control
        switchCtrlPosRef = ikCtrlRefObj

        if not ikCtrlRefObj:
            switchCtrlPosRef = endJoint

        switchCtrl = self.createControl(prefix=prefix + 'Switch', controlScale=rigScale * 4, ctrlShape="twoArrows",
                                        matchMoveObj=switchCtrlPosRef, point=True, parentObj=controlsGrp)

        sideMulti = 1
        if prefix.startswith('r_'):
            switchCtrl['c'].clsMove(-sideMulti * rigScale * 4, sideMulti * rigScale * 3, -sideMulti * rigScale * 4, r=1)
        else:
            switchCtrl['c'].clsMove(sideMulti * rigScale * 4, sideMulti * rigScale * 3, -sideMulti * rigScale * 4, r=1)
        # attach IK control
        Joint(endJoint).pointConstraint(switchCtrl['off'], mo=1)
        ikBaseGrp.parentConstraint(mainIkCtrl['off'], mo=1)
        ikBaseGrp.parentConstraint(pvCtrl['off'], mo=1)
        # make FK controls
        fkControls = []
        jointChain = [Joint(startJoint), Joint(midJoint), Joint(endJoint)]
        for i in range(len(jointChain)):
            fkCtrlPrefix = "%sFK%d" % (prefix, i + 1)
            fkCtrl = self.createControl(prefix=fkCtrlPrefix, controlScale=rigScale * 5, ctrlShape='ctrlCircle',
                                        nr=(1, 0, 0),
                                        matchMoveObj=jointChain[i], parentObj=controlsGrp)
            fkControls.append(fkCtrl)

            if i > 0:
                fkCtrl['off'].parentTo(fkControls[-2]['c'])

            if i < 2:
                fkCtrl['c'].a.r >> jointChain[i].a.r
                fkCtrl['c'].a.ro >> jointChain[i].a.ro

        if not partType == 'arm':
            baseGrp.parentConstraint(fkControls[0]['off'], mo=1)

        # setup IK FK
        ikFkAt = 'FK_IK'
        switchCtrl['c'].a.add(ln=ikFkAt, at='float', min=0, max=1, dv=1, k=1)

        mainIkHdl = Dag(cmds.ikHandle(n=prefix + 'Main_ikHdl', sol='ikRPsolver', sj=startJoint, ee=endJoint)[0])
        mainIkHdl.parentTo(mainIkCtrl['c'])
        mainIkHdl.hide()
        cmds.poleVectorConstraint(pvCtrl['c'], mainIkHdl)

        switchCtrl['c'].a[ikFkAt] >> mainIkHdl.a.ikBlend

        # IK control visibility
        switchCtrl['c'].a[ikFkAt] >> mainIkCtrl['off'].a.v
        switchCtrl['c'].a[ikFkAt] >> pvCtrl['off'].a.v

        ikFkReverseNode = Dep(prefix + 'IKFKVis_rev', nodeType="reverse")
        switchCtrl['c'].a[ikFkAt] >> ikFkReverseNode.a.ix
        ikFkReverseNode.a.ox >> fkControls[0]['off'].a.v

        # connect end joint in ikFk blend
        ikFkConstrainNode = Dag(
            cmds.parentConstraint(mainIkCtrl['c'], fkControls[2]['c'], endJoint, st=['x', 'y', 'z'], mo=1)[0])
        ikFkConstrainNode.a['interpType'].set(2)
        ikFkConstrainNodeWtAttrs = cmds.parentConstraint(ikFkConstrainNode.fullPath, q=1, weightAliasList=1)
        switchCtrl['c'].a[ikFkAt] >> ikFkConstrainNode.a[ikFkConstrainNodeWtAttrs[0]]
        ikFkReverseNode.a.ox >> ikFkConstrainNode.a[ikFkConstrainNodeWtAttrs[1]]

        # pv connection line
        midJointCtrlPos = mainIkCtrl['c'].o.position[:3]
        pvCtrlPos = pvCtrl['c'].o.position[:3]
        pvLine = Curve(cmds.curve(n=prefix + 'PvConnect_crv', d=1, p=[midJointCtrlPos, pvCtrlPos]))
        pvLine.parentTo(controlsGrp)
        pvLine.a.template.set(1)
        cmds.cluster([pvLine.fullPath + '.cv[0]'], wn=[midJoint, midJoint], bs=1)
        cmds.cluster([pvLine.fullPath + '.cv[1]'], wn=[pvCtrl['c'], pvCtrl['c']], bs=1)

        switchCtrl['c'].a[ikFkAt] >> pvLine.a.v

        # arm specific setup
        if partType == "arm":

            # make clavicle control
            clavicleCtrl = self.createControl(prefix=prefix + 'clavicle', controlScale=rigScale * 10, ctrlShape="io",
                                              matchMoveObj=clavicleJnt, point=True, parentObj=controlsGrp)
            cmds.delete(cmds.pointConstraint(clavicleJnt, startJoint, clavicleCtrl['off']))
            clavicleCtrl['c'].deleteHistory()
            cls, clsHdl = cmds.cluster(clavicleCtrl['c'], n='tempCluster')
            Dag(clsHdl).move(0, 0, 10)
            clavicleCtrl['c'].deleteHistory()
            if prefix.startswith('r_'):
                cmds.rotate(clavicleCtrl['off'], r=1)
                clavicleCtrl['c'].clsRotate(180, -180, -180, r=1)
            for ax in ['x', 'y', 'z']:
                clavicleCtrl['c'].a['t' + ax].set(l=True, k=False)
            # attach clavicle
            clavicleCtrl['c'].orientConstraint(clavicleJnt, mo=1)
            baseGrp.parentConstraint(clavicleCtrl['off'], mo=1)
            # attach FK control
            fkControls[0]['off'].parentTo(clavicleCtrl['c'])

            # make finger controls
            handJoints = Joint(endJoint).allChildren
            handJoints.reverse()
            fingerCtrls = []

            for j in handJoints:
                if not j.children:
                    continue
                CtrlPrefix = j.name.replace('_jnt', '')
                ctrl = self.createControl(prefix=CtrlPrefix, controlScale=rigScale * 1.2, ctrlShape='ctrlCircle',
                                          nr=(1, 0, 0), matchMoveObj=j, parentObj=controlsGrp)

                ctrl['c'].a.r >> j.a.r
                ctrl['c'].a.ro >> j.a.ro

                for ax in ['x', 'y', 'z']:
                    ctrl['c'].a['t' + ax].set(l=1, k=0)

                parentJnt = j.parent
                if parentJnt == endJoint:
                    Joint(endJoint).parentConstraint(ctrl['off'], mo=1)
                else:
                    ctrl['off'].parentTo(fingerCtrls[-1]['c'])

                fingerCtrls.append(ctrl)

            # scapula control
            scapulaEndJnt = Joint(scapulaJnt).children[0]
            scapulaIk = Dag(
                cmds.ikHandle(n=prefix + 'Scapula_ikh', sol='ikSCsolver', sj=scapulaJnt, ee=scapulaEndJnt)[0])
            scapulaCtrl = self.createControl(prefix=prefix + 'Scapula', controlScale=rigScale * 4,
                                             ctrlShape='ctrlCircle',
                                             nr=[1, 0, 0], matchMoveObj=scapulaEndJnt, parentObj=controlsGrp,
                                             point=True)
            scapulaIk.parentTo(partsGrp)
            scapulaCtrl['c'].pointConstraint(scapulaIk)

            baseGrp.parentConstraint(scapulaCtrl['off'], mo=1)

        # foot specific set up
        if partType == "leg":
            toeEndJnt = Joint(toeJnt).children[0]
            ballIkHdl = Dag(cmds.ikHandle(n=prefix + 'Ball_ikh', sol='ikSCsolver', sj=endJoint, ee=toeJnt)[0])
            toeIkHdl = Dag(cmds.ikHandle(n=prefix + 'Toe_ikh', sol='ikSCsolver', sj=toeJnt, ee=toeEndJnt)[0])
            ballIkHdl.hide()
            toeIkHdl.hide()

            ballIkHdl.parentTo(revJnts[-2])
            toeIkHdl.parentTo(revJnts[-3])
            mainIkHdl.parentTo(revJnts[-1])
            Joint(revJnts[0]).parentTo(mainIkCtrl['c'])
            bankInnerGrp = self.createGroup(revJnts[0], n=prefix + "bank_inner")
            bankOuterGrp = self.createGroup(bankInnerGrp, n=prefix + 'bank_outer')
            toeTapOffGrp = self.createGroup(toeIkHdl, n='toeTapOffGrp')
            bankInnerGrp.o.copyPivotFrom(bankRefLoc[0])
            bankOuterGrp.o.copyPivotFrom(bankRefLoc[1])
            toeTapOffGrp.o.copyPivotFrom(toeJnt)

            for hdl in [ballIkHdl, toeIkHdl]:
                switchCtrl['c'].a[ikFkAt] >> hdl.a['ikBlend']
            # add foot control attrs
            mainIkCtrl['c'].a.add(ln="CONTROLS", at='enum', enumName='-----------', k=0)
            mainIkCtrl['c'].a['CONTROLS'].set(cb=1, l=1)
            mainIkCtrl['c'].a.add(ln='Bank', at="float", dv=0, k=1)
            mainIkCtrl['c'].a.add(ln='heelTwist', at="float", dv=0, k=1)
            mainIkCtrl['c'].a.add(ln='toeTwist', at="float", dv=0, k=1)
            mainIkCtrl['c'].a.add(ln='toeTap', at="float", dv=0, k=1)
            mainIkCtrl['c'].a.add(ln='footRoll', at="float", dv=0, min=-10, max=10, k=1)

            # set foot control attrs
            mainIkCtrl['c'].a['heelTwist'] >> Joint(revJnts[0]).a.ry
            mainIkCtrl['c'].a['toeTwist'] * (-1) >> Joint(revJnts[1]).a.ry
            mainIkCtrl['c'].a['toeTap'] * (-1) >> toeTapOffGrp.a.rx
            # set foot roll
            mainIkCtrl['c'].a['footRoll'].set(-10)
            Joint(revJnts[0]).a.rx.set(-40)
            cmds.setDrivenKeyframe(revJnts[0] + '.rotateX', cd=mainIkCtrl['c'].a['footRoll'])
            mainIkCtrl['c'].a['footRoll'].set(0)
            Joint(revJnts[0]).a.rx.set(0)
            cmds.setDrivenKeyframe(revJnts[0] + '.rotateX', cd=mainIkCtrl['c'].a['footRoll'])

            mainIkCtrl['c'].a['footRoll'].set(0)
            Joint(revJnts[2]).a.rx.set(0)
            cmds.setDrivenKeyframe(revJnts[2] + '.rotateX', cd=mainIkCtrl['c'].a['footRoll'])
            mainIkCtrl['c'].a['footRoll'].set(5)
            Joint(revJnts[2]).a.rx.set(40)
            cmds.setDrivenKeyframe(revJnts[2] + '.rotateX', cd=mainIkCtrl['c'].a['footRoll'])
            mainIkCtrl['c'].a['footRoll'].set(10)
            Joint(revJnts[2]).a.rx.set(0)
            cmds.setDrivenKeyframe(revJnts[2] + '.rotateX', cd=mainIkCtrl['c'].a['footRoll'])

            mainIkCtrl['c'].a['footRoll'].set(10)
            Joint(revJnts[1]).a.rx.set(40)
            cmds.setDrivenKeyframe(revJnts[1] + '.rotateX', cd=mainIkCtrl['c'].a['footRoll'])
            mainIkCtrl['c'].a['footRoll'].set(5)
            Joint(revJnts[1]).a.rx.set(0)
            cmds.setDrivenKeyframe(revJnts[1] + '.rotateX', cd=mainIkCtrl['c'].a['footRoll'])

            mainIkCtrl['c'].a['footRoll'].set(0)

            # set bank
            BankConditionNode = (mainIkCtrl['c'].a['Bank'] > 0).node

            mainIkCtrl['c'].a['Bank'] >> BankConditionNode.a['colorIfTrueR']
            mainIkCtrl['c'].a['Bank'] >> BankConditionNode.a['colorIfFalseG']

            if prefix.startswith('l_'):
                BankConditionNode.a.outColorR >> bankInnerGrp.a.rz
                BankConditionNode.a.outColorG >> bankOuterGrp.a.rz
            else:
                BankConditionNode.a.outColorR * (-1) >> bankInnerGrp.a.rz
                BankConditionNode.a.outColorG * (-1) >> bankOuterGrp.a.rz

            # add toe FK control
            toeFkCtrlPrefix = '{0}Fk{1}'.format(prefix, len(fkControls) + 1)
            toeFkCtrl = self.createControl(prefix=toeFkCtrlPrefix, controlScale=rigScale * 4, ctrlShape="ctrlCircle",
                                           nr=(1, 0, 0),
                                           matchMoveObj=toeJnt, parentObj=fkControls[-1]['c'])

            toeFkCtrl['c'].a.r >> Joint(toeJnt).a.r
            toeFkCtrl['c'].a.ro >> Joint(toeJnt).a.ro

        # ------------- #
        # stretch setup #
        # ------------- #

        if addStretch:

            # IK stretch
            stretchPrefix = prefix + 'Stretch_'

            attachObj = baseGrp
            if partType == 'arm':
                attachObj = clavicleJnt
            # measure length of arm joints
            upperArmLength = Joint(startJoint).o.distanceTo(midJoint)
            lowerArmLength = Joint(midJoint).o.distanceTo(endJoint)
            startEndLength = Joint(startJoint).o.distanceTo(endJoint)

            armLength = upperArmLength + lowerArmLength

            # adjust minimum stretch length to prevent IK popping
            minStretchLength = armLength * 0.995

            # prevent higher default scale
            if minStretchLength < startEndLength:
                minStretchLength = startEndLength

            # build measure groups
            stretchAimGrp = self.createGroup(n=stretchPrefix + 'IkAim_grp', em=1, p=startJoint)
            stretchAimGrp.parentTo(partsGrp)
            Dag(attachObj).parentConstraint(stretchAimGrp, mo=1, sr=('x', 'y', 'z'))
            cmds.aimConstraint(mainIkCtrl['c'], stretchAimGrp, aim=[1, 0, 0], wut='none')

            # scale stretch group to start of stretch length
            stretchAimGrp.a.sx.set(minStretchLength)

            stretchPointGrp = self.createGroup(n=stretchPrefix + 'IkPoint_grp', em=1, p=stretchAimGrp)
            stretchAimGrp.a.tx.set(1)
            mainIkCtrl['c'].pointConstraint(stretchPointGrp)

            # add stretch multi attribute
            stretchMultiAt = 'stretchMulti'
            switchCtrl['c'].a.add(ln=stretchMultiAt, at='float', min=0, max=1, dv=1, k=1)

            # connect stretch point position to arm joints scale X
            scaleClampNode = Dep(stretchPrefix + 'Scale_clp', nodeType='clamp')
            scaleClampNode.a['minR'].set(1)
            scaleClampNode.a['maxR'].set(1000)
            stretchPointGrp.a.tx >> scaleClampNode.a['inputR']

            ikStretchBlendNode = Dep(stretchPrefix + 'Multi_bta', nodeType='blendTwoAttr')
            switchCtrl['c'].a[stretchMultiAt] >> ikStretchBlendNode.a['attributesBlender']
            ikStretchBlendNode.a['input[0]'].set(1)
            scaleClampNode.a['outputR'] >> ikStretchBlendNode.a['input']

            # FK stretch
            fkUpperStretchAt = 'fkUpperStretch'
            fkLowerStretchAt = 'fkLowerStretch'
            for at in [fkUpperStretchAt, fkLowerStretchAt]:
                switchCtrl['c'].a.add(ln=at, at='float', min=0.5, max=2, dv=1, k=1)

            for jnt, armPart, fkAt in zip([startJoint, midJoint], ['Upper', 'Lower'],
                                          [fkUpperStretchAt, fkLowerStretchAt]):
                ikFkStretchBlendNode = Dep(stretchPrefix + 'IkFK%s_bta' % armPart, nodeType='blendTwoAttr')

                switchCtrl['c'].a[ikFkAt] >> ikFkStretchBlendNode.a['attributesBlender']
                switchCtrl['c'].a[fkAt] >> ikFkStretchBlendNode.a.input
                ikStretchBlendNode.a.o >> ikFkStretchBlendNode.a.input

                ikFkStretchBlendNode.a.o >> Joint(jnt).a.sx

            # attach FK controls to joint
            Joint(midJoint).pointConstraint(fkControls[1]['off'])
            Joint(endJoint).pointConstraint(fkControls[2]['off'])

        if makeTwistJoints:
            for joint in [Joint(j) for j in cmds.ls(type='joint')]:
                joint.a.s.set(1, 1, 1)
            tools.twistJointsSetUp(prefix=prefix, moduleObjs=moduleObjs, partType=partType, startJoint=startJoint,
                                   midJoint=midJoint, endJoint=endJoint, clavicleJnt=clavicleJnt, baseGrp=baseGrp)

        return {
            'mainGrp': mainGrp,
            'moduleObjs': moduleObjs,
            'baseGrp': baseGrp,
            'ikBaseGrp': ikBaseGrp
        }

    def hiresWrapModel(self, baseGroupData):
        """
        add high resolution model objects to rig and wrap them to proxy meshes
        """
        jawCtrl = Curve('head_Jaw_ctrl')
        jawCtrl.a.rz.set(-8)
        wrapBls = 'body_wrap_bls'
        cmds.setAttr(wrapBls + '.openMouthWrap', 1)

        hiresPrefix = 'hires_'
        wrapDriverGeos = ['body_geo', 'cloth_geo', 'belt_geo', 'ring_geo']
        wrapperGeosGrp = Dag(cmds.group(n='wrapperGeos_grp', em=True, p=baseGroupData['topGrp']))
        wrapperGeosGrp.hide()

        for geo in wrapDriverGeos:
            Mesh(geo).parentTo(wrapperGeosGrp)

            hiresGeo = Mesh(hiresPrefix + geo)
            hiresGeo.parentTo(baseGroupData['modelGrp'])

            hiresGeo.deleteHistory()

            cmds.select(hiresGeo.fullPath)
            cmds.select(geo, add=True)
            mel.eval('doWrapArgList "7" { "1","0","1", "2", "1", "1", "0", "0" }')

        jawCtrl.a.rz.set(0)

        hiresModelGrp = Dag(hiresPrefix + self.charName + '_grp')
        hiresModelGrp.delete()

    def saveSkinWeights(self, modelGrp, weightsPath='%sweights/'):
        """save all meshes' skin weights to specified folder"""
        modelGrp = Dag(modelGrp)
        modelGeos = [cmds.listRelatives(m, p=True)[0] for m in cmds.listRelatives(modelGrp, ad=True, type='mesh')]
        modelGeos = list(set(modelGeos))
        projectFolder = self.projectPath % (self.type, self.charName)
        weightsFolder = weightsPath % projectFolder

        for mesh in modelGeos:
            Mesh(mesh).saveSkinWeights(weightsFolder)

    def loadSkinWeights(self, modelGrp, weightsPath='%sweights/'):
        """load all meshes' skin weights from specified folder"""
        modelGrp = Dag(modelGrp)
        modelGeos = [cmds.listRelatives(m, p=True)[0] for m in cmds.listRelatives(modelGrp, ad=True, type='mesh')]
        modelGeos = list(set(modelGeos))

        projectFolder = self.projectPath % (self.type, self.charName)
        weightsFolder = weightsPath % projectFolder

        for mesh in modelGeos:
            Mesh(mesh).loadSkinWeights(weightsFolder)


if __name__ == '__main__':
    setup('biped', 'troll')
