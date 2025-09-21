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

// Убираем pdoFetch полностью - используем только getCollection

// Получаем параметры
$limit = $modx->getOption('limit', $scriptProperties, 1000); // Большой лимит для всех продуктов
$category = isset($_GET['category']) ? $_GET['category'] : '';

// Отладочная информация (можно убрать в продакшене)
// $debug_info = array(
//     'category_param' => $category,
//     'scriptProperties' => $scriptProperties,
//     'get_params' => $_GET
// );

// Получаем продукты - если категория не указана, получаем все категории
if (!empty($category)) {
    // Запрос для конкретной категории
    $sql = "SELECT 
        p.id, p.pagetitle, p.alias, p.template, p.published, p.parent,
        d.price, d.weight, d.source,
        parent.pagetitle as category_name
    FROM {$modx->getTableName('modResource')} p
    LEFT JOIN {$modx->getTableName('msProductData')} d ON d.id = p.id
    LEFT JOIN {$modx->getTableName('modResource')} parent ON parent.id = p.parent
    WHERE p.class_key = 'msProduct' 
        AND p.published = 1 
        AND p.deleted = 0
        AND p.parent = " . intval($category) . "
    ORDER BY p.id ASC";
    
    if ($limit > 0) {
        $sql .= " LIMIT " . intval($limit);
    }
    
    $stmt = $modx->prepare($sql);
    $stmt->execute();
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
} else {
    // Запрос для всех категорий - получаем по категориям
    $rows = array();
    $categories = array(16, 17, 18, 19); // Известные категории
    
    foreach ($categories as $cat_id) {
        $sql = "SELECT 
            p.id, p.pagetitle, p.alias, p.template, p.published, p.parent,
            d.price, d.weight, d.source,
            parent.pagetitle as category_name
        FROM {$modx->getTableName('modResource')} p
        LEFT JOIN {$modx->getTableName('msProductData')} d ON d.id = p.id
        LEFT JOIN {$modx->getTableName('modResource')} parent ON parent.id = p.parent
        WHERE p.class_key = 'msProduct' 
            AND p.published = 1 
            AND p.deleted = 0
            AND p.parent = " . intval($cat_id) . "
        ORDER BY p.id ASC";
        
        $stmt = $modx->prepare($sql);
        $stmt->execute();
        $cat_rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $rows = array_merge($rows, $cat_rows);
    }
    
    // Применяем общий лимит если нужно
    if ($limit > 0 && count($rows) > $limit) {
        $rows = array_slice($rows, 0, $limit);
    }
}

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
            'products' => $output,
            'debug' => $debug_info
        ];

return json_encode($result, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
?>

