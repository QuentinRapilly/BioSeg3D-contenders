# Aide pour utiliser omnipose

## Entrainement

Utiliser la commande présente sur le git :
```
omnipose --use_gpu --train --dir <path> --mask_filter _masks --n_epochs 4000 --pretrained_model None --learning_rate 0.1 --save_every 50 --save_each  --verbose --look_one_level_down --all_channels --dim 3 --batch_size 1 --diameter 0 --nclasses 2
```

Pour entrainer les donnees doivent avoir un format particulier : les images et les masques doivent être dans le même dossier. Un masque doit avoir le même nom que son image avec à la fin du nom le "mask_filter" choisi (ex: nom_img_mask_filter.tif).

L'optimizer RAdam n'a pas l'air de fonctionner.

## Inference

L'utilisation de l'argument tiles ne semble pas fonctionner. Ainsi, je n'ai pas encore trouvé de moyen de faire d'inférence si l'image entière nécessite plus de mémoire que ce qui est présent sur le GPU.
