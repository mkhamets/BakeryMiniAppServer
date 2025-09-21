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

// Получаем параметры
$limit = $modx->getOption('limit', $scriptProperties, 10);
$category = isset($_GET['category']) ? $_GET['category'] : '';

// Отладочная информация (можно убрать в продакшене)
// $debug_info = array(
//     'category_param' => $category,
//     'scriptProperties' => $scriptProperties,
//     'get_params' => $_GET
// );

// Получаем продукты
$where = array(
    'class_key' => 'msProduct',
    'published' => 1,
    'deleted' => 0
);

if (!empty($category)) {
    $where['parent'] = $category;
}

$leftJoin = array(
    'Data' => array('class' => 'msProductData'),
    'Parent' => array('class' => 'modResource', 'on' => 'Parent.id = msProduct.parent'),
);

$select = array(
    'msProduct' => $modx->getSelectColumns('msProduct', 'msProduct', '', array('content'), true),
    'Data' => $modx->getSelectColumns('msProductData', 'Data', '', array('id'), true),
    'Parent' => $modx->getSelectColumns('modResource', 'Parent', 'category_', array('id'), true),
);

$default = array(
    'class' => 'msProduct',
    'where' => $where,
    'leftJoin' => $leftJoin,
    'select' => $select,
    'sortby' => 'msProduct.id',
    'sortdir' => 'ASC',
    'limit' => $limit,
    'return' => 'data',
);

$pdoFetch->setConfig(array_merge($default, $scriptProperties), false);
$rows = $pdoFetch->run();

// Обрабатываем результаты
$output = array();
if (!empty($rows) && is_array($rows)) {
    foreach ($rows as $k => $row) {
        $product_id = $row['id'];
        
        // Получаем TV поля (Template Variables)
        $tv_fields = array(
            'product_description',
            'product_days_order', 
            'product_structure',
            'product_calories',
            'product_bgu',
            'product_vegan'
        );
        
        $tv_data = array();
        foreach ($tv_fields as $tv_name) {
            $tv = $modx->getObject('modTemplateVar', array('name' => $tv_name));
            if ($tv) {
                $tv_resource = $modx->getObject('modTemplateVarResource', array(
                    'contentid' => $product_id,
                    'tmplvarid' => $tv->get('id')
                ));
                $tv_data[$tv_name] = $tv_resource ? $tv_resource->get('value') : '';
            } else {
                $tv_data[$tv_name] = '';
            }
        }
        
                // Получаем изображения продукта (только основные, без размеров)
                $product_images = array();
                $file_query = $modx->newQuery('msProductFile');
                $file_query->where([
                    'product_id' => $product_id,
                    'type' => 'image'
                ]);
                $file_query->sortby('rank', 'ASC');
                
                $files = $modx->getCollection('msProductFile', $file_query);
                foreach ($files as $file) {
                    $url = $file->get('url');
                    // Пропускаем изображения с размерами (thumb, small, medium, large, extralarge)
                    if (strpos($url, '/thumb/') === false && 
                        strpos($url, '/small/') === false && 
                        strpos($url, '/medium/') === false && 
                        strpos($url, '/large/') === false && 
                        strpos($url, '/extralarge/') === false) {
                        $product_images[] = 'https://drazhin.by/' . ltrim($url, '/');
                    }
                }
        
        // Формируем результат
        $result_item = array(
            'id' => $row['id'],
            'pagetitle' => $row['pagetitle'],
            'alias' => $row['alias'],
            'template' => $row['template'],
            'published' => $row['published'] ? 'yes' : 'no',
            'parent' => $row['category_pagetitle'] ?? '',
            'parent_id' => $row['parent'],
            'price' => $miniShop2->formatPrice($row['price']),
            'weight' => $miniShop2->formatWeight($row['weight']),
            'source' => $row['source'] ?? '',
            'image' => !empty($product_images) ? $product_images[0] : '',
            'images' => $product_images,
        );
        
        // Добавляем TV поля
        $result_item = array_merge($result_item, $tv_data);
        
        $output[] = $result_item;
    }
}

        $result = [
            'status' => 'success',
            'count' => count($output),
            'products' => $output
        ];

return json_encode($result, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
?>

