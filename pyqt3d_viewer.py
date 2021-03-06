import sys

from PyQt5.QtCore import pyqtSlot, QObject, QSize, Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QColor, QQuaternion, QVector3D, QMatrix4x4, QImage, QGuiApplication, QKeySequence

from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QCommandLinkButton, QMenu,
        QHBoxLayout, QVBoxLayout, QWidget, QMainWindow, QShortcut, QPushButton)

from PyQt5.Qt3DCore import QEntity, QTransform

from PyQt5.Qt3DExtras import (Qt3DWindow, QDiffuseMapMaterial,
        QFirstPersonCameraController, QNormalDiffuseMapAlphaMaterial,
        QNormalDiffuseMapMaterial, QNormalDiffuseSpecularMapMaterial,
        QPhongMaterial, QPlaneMesh)

from PyQt5.Qt3DInput import QInputAspect
from PyQt5.Qt3DRender import QCamera, QCameraLens, QMesh, QTextureImage, QPointLight

class PlaneEntity(QEntity):

    def __init__(self, parent=None):
        super(PlaneEntity, self).__init__(parent)

        self.m_mesh = QPlaneMesh()
        self.m_transform = QTransform()

        self.addComponent(self.m_mesh)
        self.addComponent(self.m_transform)

    def mesh(self):
        return self.m_mesh


class RenderableEntity(QEntity):

    def __init__(self, parent=None):
        super(RenderableEntity, self).__init__(parent)

        self.m_mesh = QMesh()
        self.m_transform = QTransform()

        self.addComponent(self.m_mesh)
        self.addComponent(self.m_transform)

    def mesh(self):
        return self.m_mesh

    def transform(self):
        return self.m_transform

class MainObject(QEntity):

    def __init__(self, parent=None):
        super(MainObject, self).__init__(parent)

        self.m_object = RenderableEntity(self)

        self.m_objectMaterial = QNormalDiffuseMapMaterial()

        self.m_objectImage = QTextureImage()
        self.m_objectNormalImage = QTextureImage()

        self.m_object.addComponent(self.m_objectMaterial)

        self.m_object.mesh().setSource(QUrl.fromLocalFile('output.obj'))

        self.m_objectMaterial.diffuse().addTextureImage(self.m_objectImage)
        self.m_objectMaterial.normal().addTextureImage(self.m_objectNormalImage)

        self.m_objectImage.setSource( QUrl.fromLocalFile('output_color.png') )
        self.m_objectNormalImage.setSource( QUrl.fromLocalFile('qt_3dviewer/exampleresources/normal.png') )
    
        self.m_objectMaterial.setShininess(80.0)
        self.m_objectMaterial.setSpecular(QColor.fromRgbF(1.0, 1.0, 1.75, 1.0))

    def setPosition(self, pos):
        self.m_object.transform().setTranslation(pos)

    def position(self):
        return self.m_object.transform().translation()

    def setScale(self, scale):
        self.m_object.transform().setScale(scale)

    def scale(self):
        return self.m_object.transform().scale()


class SceneModifier(QObject):

    def __init__(self, rootEntity):
        super(SceneModifier, self).__init__()

        self.m_rootEntity = rootEntity

        self.normalDiffuseSpecularMapMaterial = QNormalDiffuseSpecularMapMaterial()
        self.normalDiffuseSpecularMapMaterial.setTextureScale(1.0)
        self.normalDiffuseSpecularMapMaterial.setShininess(80.0)
        self.normalDiffuseSpecularMapMaterial.setAmbient(QColor.fromRgbF(1.0, 1.0, 1.0, 1.0))

        diffuseImage = QTextureImage()
        diffuseImage.setSource( QUrl.fromLocalFile('output.png') )
        self.normalDiffuseSpecularMapMaterial.diffuse().addTextureImage(diffuseImage)
        background = QImage()
        background.load('output.png')

        # Background Plane
        self.planeEntity = PlaneEntity(self.m_rootEntity)
        self.planeEntity.mesh().setHeight(20.0)
        self.planeEntity.mesh().setWidth(20.0 * background.width() / background.height())
        self.planeEntity.mesh().setMeshResolution(QSize(5, 5))

        self.planeEntity.addComponent(self.normalDiffuseSpecularMapMaterial)

        self.obj = MainObject(self.m_rootEntity)
        self.obj.setPosition(QVector3D(0.0, 5.0, 0.0))
        self.obj.setScale(0.05)

    @pyqtSlot()
    def transformLeft(self):
        self.obj.setPosition(self.obj.position() + QVector3D(0.5, 0.0, 0.0))

    @pyqtSlot()
    def transformRight(self):
        self.obj.setPosition(self.obj.position() - QVector3D(0.5, 0.0, 0.0))
        print(self.obj.position())

    @pyqtSlot()
    def transformUp(self):
        self.obj.setPosition(self.obj.position() + QVector3D(0.0, 0.0, 0.5))

    @pyqtSlot()
    def transformDown(self):
        self.obj.setPosition(self.obj.position() - QVector3D(0.0, 0.0, 0.5))
    
    @pyqtSlot()
    def scaleUp(self):
        self.obj.setScale(self.obj.scale() + 0.005)

    @pyqtSlot()
    def scaleDown(self):
        self.obj.setScale(self.obj.scale() - 0.005)

app = QApplication(sys.argv)

view = Qt3DWindow()
# view.defaultFramegraph().setClearColor(QColor(0x4d4d4f))
container = QWidget.createWindowContainer(view)
screenSize = view.screen().size()
container.setMinimumSize(QSize(200, 100))
container.setMaximumSize(screenSize)

widget = QWidget()
hLayout = QHBoxLayout(widget)
vLayout = QVBoxLayout()
vLayout.setAlignment(Qt.AlignTop)
hLayout.addWidget(container, 1)
hLayout.addLayout(vLayout)

widget.setWindowTitle("3D Viewer")

aspect = QInputAspect()
view.registerAspect(aspect)

# Root entity.
rootEntity = QEntity()

# Camera.
cameraEntity = view.camera()

cameraEntity.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
cameraEntity.setPosition(QVector3D(0.0, 24.0, -0.5))
cameraEntity.setUpVector(QVector3D(0.0, 1.0, 0.0))
cameraEntity.setViewCenter(QVector3D(0.0, 0.0, 0.0))

# Light
lightEntity = QEntity(rootEntity)
light = QPointLight(lightEntity)
light.setColor(QColor.fromRgbF(1.0, 1.0, 1.0, 1.0))
light.setIntensity(1)
lightEntity.addComponent(light)
lightTransform = QTransform(lightEntity)
lightTransform.setTranslation(QVector3D(10.0, 40.0, 0.0))
lightEntity.addComponent(lightTransform)

# For camera controls.
camController = QFirstPersonCameraController(rootEntity)
camController.setCamera(cameraEntity)

# Scene modifier.
modifier = SceneModifier(rootEntity)

moveLeft = QPushButton(text="Left")
moveLeft.clicked.connect(modifier.transformLeft)
moveLeft.setAutoRepeat(True)

moveRight = QPushButton(text="Right")
moveRight.clicked.connect(modifier.transformRight)
moveRight.setAutoRepeat(True)

moveUp = QPushButton(text="Up")
moveUp.clicked.connect(modifier.transformUp)
moveUp.setAutoRepeat(True)

moveDown = QPushButton(text="Down")
moveDown.clicked.connect(modifier.transformDown)
moveDown.setAutoRepeat(True)

scaleDown = QPushButton(text="Scale Down")
scaleDown.clicked.connect(modifier.scaleDown)
scaleDown.setAutoRepeat(True)

scaleUp = QPushButton(text="Scale Up")
scaleUp.clicked.connect(modifier.scaleUp)
scaleUp.setAutoRepeat(True)

vLayout.addWidget(moveLeft)
vLayout.addWidget(moveRight)
vLayout.addWidget(moveUp)
vLayout.addWidget(moveDown)
vLayout.addWidget(scaleUp)
vLayout.addWidget(scaleDown)

# Set root object of the scene.
view.setRootEntity(rootEntity)

# Show the window.
widget.show()
widget.resize(1200, 800)

sys.exit(app.exec_())
