[toc]

# apk 可执行文件

## apk 文件结构

- META-INF

   > 目录下存放的签名信息，用来保证apk包的完整性和系统安全性
   >
   > 软件编译时生成，软件安装时校验
   >
   > 软件修改后需要将里面的证书文件删除（.RSA、.SF、.MF三个文件），否则软件无法安装。

- res
   
   > 存放资源文件
   
   - anim
   
     > XML文件，它们被编译进逐帧动画（frame by frameanimation）或补间动画(tweenedanimation)对象
   
   - color
   
   - drawable
   
     > .png、.9.png、.jpg文件，它们被编译进以下的Drawable资源子类型中：
     >
     > 要获得这种类型的一个资源，可以使用Resource.getDrawable(*id*)
   
   - drawable-hdpi
   
   - drawable-land
   
   - drawable-land-hdpi
   
   - drawable-mdpi
   
   - drawable-port
   
   - drawable-port-hdpi
   
   - layout
   
     > 被编译为屏幕布局(或屏幕的一部分)的XML文件
   
   - layout-land
   
   - layout-port
   
   - xml
   
- AndroidManifest.xml

   > 每个应用都必须包含，它描述了应用的名字、版本、权限、引用的库文件等信息
   >
   > 在apk中AndroidManifest.xml是经过压缩的，可以通过AXMLPrinter2工具解压

- classes.dex

   > 在Android系统中，dex文件是可以直接在Dalvik虚拟机中加载运行的文件
   >
   > ![](https://blog-1308247953.cos.ap-chengdu.myqcloud.com/blog/20130723222746531.png)
   >
   > - dex文件整体结构
   >
   >   ```c++
   >   typedef struct DexFile {
   >       /* directly-mapped "opt" header */
   >       const DexOptHeader* pOptHeader;
   >       /* pointers to directly-mapped structs and arrays in base DEX */
   >       const DexHeader*    pHeader;
   >       const DexStringId*  pStringIds;
   >       const DexTypeId*    pTypeIds;
   >       const DexFieldId*   pFieldIds;
   >       const DexMethodId*  pMethodIds;
   >       const DexProtoId*   pProtoIds;
   >       const DexClassDef*  pClassDefs;
   >       const DexLink*      pLinkData;
   >       /* mapped in "auxillary" section */
   >       const DexClassLookup* pClassLookup;
   >       /* mapped in "auxillary" section */
   >       DexIndexMap         indexMap;
   >       /* points to start of DEX file data */
   >       const u1*           baseAddr;
   >       /* track memory overhead for auxillary structures */
   >       int                 overhead;
   >       /* additional app-specific data structures associated with the DEX */
   >       //void*               auxData;
   >   } DexFile;
   >   ```
   >
   > - dex文件头
   >
   >   ```c++
   >   typedef struct DexHeader {
   >       u1  magic[8];           /* includes version number */
   >       u4  checksum;           /* adler32 checksum */
   >       u1  signature[kSHA1DigestLen]; /* SHA-1 hash */
   >       u4  fileSize;           /* length of entire file */
   >       u4  headerSize;         /* offset to start of next section */
   >       u4  endianTag;
   >       u4  linkSize;
   >       u4  linkOff;
   >       u4  mapOff;
   >       u4  stringIdsSize;
   >       u4  stringIdsOff;
   >       u4  typeIdsSize;
   >       u4  typeIdsOff;
   >       u4  protoIdsSize;
   >       u4  protoIdsOff;
   >       u4  fieldIdsSize;
   >       u4  fieldIdsOff;
   >       u4  methodIdsSize;
   >       u4  methodIdsOff;
   >       u4  classDefsSize;
   >       u4  classDefsOff;
   >       u4  dataSize;
   >       u4  dataOff;
   >   } DexHeader;
   >   ```
   >
   >   

- resources.arsc

> 编译后的二进制资源文件。通常本地化、汉化资源存储在该文件文件中。