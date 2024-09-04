# test

# add

- fade_transition
- drag & drop


# notes

- spriteがsurfaceを直接参照するか否か？
  - 関節参照であれば絵の切り替えが容易に？
  - sprite sheet は？
- sceneの切り替え
  - sceneが始まる度に新しいexecutorのインスタンス？
  - `executor(draw_target)`
  - `Transition(...)(from_: Surface, to_: Surface)`
- 重なり順の動的変更
  - タスクを再起動？
    - 重なり順を変える度に仕切り直されるのは不都合
- android上で動的にパッケージ内のモジュールを列挙
  - [importlib.resources](https://docs.python.org/3/library/importlib.resources.html#module-importlib.resources) ?
