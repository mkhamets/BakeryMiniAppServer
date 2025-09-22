<?php
/** @var modX $modx */
/** @var array $scriptProperties */

// Устанавливаем заголовки для JSON
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Инициализируем miniShop2
$miniShop2 = $modx->getService('miniShop2');
if (!($miniShop2 instanceof miniShop2)) {
    return json_encode(['error' => 'miniShop2 не найден'], JSON_UNESCAPED_UNICODE);
}
$miniShop2->initialize($modx->context->key);

// Инициализируем pdoFetch
$fqn = $modx->getOption('pdoFetch.class', null, 'pdotools.pdofetch', true);
$path = $modx->getOption('pdofetch_class_path', null, MODX_CORE_PATH . 'components/pdotools/model/', true);

if ($pdoClass = $modx->loadClass($fqn, $path, false, true)) {
    $pdoFetch = new $pdoClass($modx, $scriptProperties);
} else {
    return json_encode(['error' => 'pdoFetch не найден'], JSON_UNESCAPED_UNICODE);
}

// Получаем категории
$where = array(
    'class_key' => 'msCategory',
    'published' => 1,
    'deleted' => 0
);

$leftJoin = array(
    'Products' => array('class' => 'msProduct', 'on' => 'Products.parent = modResource.id AND Products.published = 1 AND Products.deleted = 0'),
);

$select = array(
    'modResource' => $modx->getSelectColumns('modResource', 'modResource', '', array('content'), true),
);

$default = array(
    'class' => 'modResource',
    'where' => $where,
    'leftJoin' => $leftJoin,
    'select' => $select,
    'sortby' => 'modResource.menuindex',
    'sortdir' => 'ASC',
    'groupby' => 'modResource.id',
    'return' => 'data',
);

$pdoFetch->setConfig(array_merge($default, $scriptProperties), false);
$rows = $pdoFetch->run();

// Обрабатываем результаты
$output = array();
if (!empty($rows) && is_array($rows)) {
    foreach ($rows as $k => $row) {
        $category_id = $row['id'];
        
        // Получаем первое изображение из первого продукта в категории
        $category_image = '';
        $first_product_query = $modx->newQuery('msProduct');
        $first_product_query->where([
            'parent' => $category_id,
            'published' => 1,
            'deleted' => 0
        ]);
        $first_product_query->limit(1);
        
        $first_product = $modx->getObject('msProduct', $first_product_query);
        if ($first_product) {
            // Получаем изображения продукта
            $file_query = $modx->newQuery('msProductFile');
            $file_query->where([
                'product_id' => $first_product->get('id'),
                'type' => 'image'
            ]);
            $file_query->limit(1);
            
            $file = $modx->getObject('msProductFile', $file_query);
            if ($file) {
                $category_image = 'https://drazhin.by/' . ltrim($file->get('url'), '/');
            }
        }
        
        $output[] = [
            'id' => $category_id,
            'name' => $row['pagetitle'],
            'description' => $row['description'],
            'uri' => $row['uri'],
            'image' => $category_image,
            'key' => 'category_' . $category_id,
            'menuindex' => $row['menuindex']
        ];
    }
}

// Сортируем категории по menuindex
usort($output, function($a, $b) {
    return $a['menuindex'] - $b['menuindex'];
});

$result = [
    'status' => 'success',
    'count' => count($output),
    'categories' => $output
];

return json_encode($result, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
?>

