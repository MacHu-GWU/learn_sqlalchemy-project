Cascades (级联)
==============================================================================

简单来说, 你对一个对象进行 Write 操作, 如果这个对象的某一个属性是用 Foreign Key 连接起来的另一个对象或是对象的列表, 这时你是否也修改这个被级联的对象? 如果是, 怎么修改? 这个问题就叫做 Cascades Update.

Sqlalchemy 提供了一下几种 Cascades 的模式:

- save-update
- delete
- delete-orphan
- merge
- refresh-expire
- expunge

默认值是 save-update, merge.
