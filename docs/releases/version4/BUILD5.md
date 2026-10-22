# iOS 1.0.0（5）与配套云端修复

2026-10-22，分支 `fix/version4-evidence-preflight`。保留 `main`、`版本4` 和构建4归档。

## 本次交付

- BFF与Worker已部署为 `v4-7c6d8fd-build5-20261022`，运行源码来自 `7c6d8fd`。数据库新增可空 `input_fingerprint`，先迁移再启用新Worker。旧任务、数据库、对象存储、额度与账号配置保留。
- iOS构建号由4改为5，已完成Xcode Release / iphoneos arm64签名归档。Bundle ID为`com.nexleap.diaryone.dev`，团队Gordon Xing / `P34R385KJ5`。
- 仍使用MobileCLIP-S0 FP16 v07、R5_18 / qwen3.8-flash、`https://bff.diary.luxe`。App共享Token为空；服务器凭据没有加入源码或安装包。
- 尚未上传TestFlight，没有在真实iPhone安装构建5。归档不是可直接安装的IPA。

## 修复进入了哪里

云端包括图片真实格式/尺寸/摘要/完整性预检、重复提交输入绑定、任务归属验证、保存失败额度补偿及原子持久化。BFF与Worker运行相同镜像，两容器各48份运行文件逐一匹配当前提交。工程恢复的具体行为与持续故障限制见[任务可靠性说明](JOB_RELIABILITY.md)。

App包含明确的上传错误与恢复提示，服务端暂时不可用时保留原任务和登录信息。此前照片归一化、视频导入反馈、Chapter/Aha展示、全屏播放与退出后保留进度继续保留。

云算法68份运行源码、合同与服务依赖清单与本地相同；`pyproject.toml`仅有本地新增的Python >=3.13条件依赖`legacy-cgi`差异，线上为Python3.10，不影响当前运行。此次没有更换算法或触发付费内容生成评测。

## 验证

| 范围 | 结果 |
|---|---|
| 修复阶段BFF回归 | 170通过，7个不适用运行时组合跳过 |
| 本机真实PostgreSQL/版本化MinIO故障测试 | 6组通过，包括迁移、并发复用、冲突、回滚和丢失提交回执 |
| 构建5 App核心 | 201通过 |
| 类型检查 / lint | 通过；0错误、4个既有警告 |
| 原生配置 / ONNX生命周期与补丁 | 4通过 / 21通过 |
| 签名归档与资源 | 27项通过，包括构建号、团队、Apple登录权限、模型摘要、新错误提示、原生模块和主App dSYM |
| 部署后HTTPS上传边界 | 5类异常请求均422；无鉴权401；任务数、对象版本数、额度摘要不变，0模型调用 |

线上异常输入为合成768×1024图片，分别注入错误尺寸、PNG伪装JPEG、错误SHA、JPEG截断和偏好JSON错误。请求经过公网HTTPS域名及真实鉴权，没有修改运行时处理函数、关闭审核或伪造生成成功。

服务器通过公网域名的HTTPS健康与上传检查正常；本次Mac直连该域名出现TLS连接重置，尚未确定本机/网络原因。不能据服务器检查声称员工手机网络已通过。新包仍需在iPhone确认登录、照片/视频导入、生成保存和播放。

## 分发

本机交付目录：`deliverables/DiaryOne-iOS-beta-build5-20261022/`，含新`.xcarchive`入口、匹配源码ZIP、校验摘要和归档检查结果。原始证据独立存放在工作区`work_logs/evidence/version4-release-build5-20261022/`，不进入运行模块。

打开构建5归档，在Xcode Organizer选择 **Distribute App → TestFlight Internal Only**，沿用已授权团队上传。App Store Connect处理完成后，将构建5加入原内部测试组。上传是后续步骤，本次没有执行。

React、ReactNativeDependencies、hermesvm三个预编译依赖仍缺匹配完整dSYM；主App符号匹配。此前这类问题表现为上传符号警告，不能据此把崩溃符号覆盖写成完整。

## 回退与仍未覆盖的情况

服务器保留旧镜像、源码、Compose覆盖文件、BFF持久化数据及PostgreSQL备份。回退应恢复旧BFF/Worker镜像和覆盖文件；新增可空列可保留，避免删除新数据。具体服务器备份位置与部署日志保存在独立工作证据，不包含在公开仓库中。

本次不声称真机/Android/BLE验收通过，也不重复宣称生成内容质量全部合格。数据库提交后持续不可查询、介质持续不可写等双重故障仍需运维核对，详见可靠性说明。
