CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `erwin`@`%` 
    SQL SECURITY DEFINER
VIEW `dunasdb`.`vouchercaja` AS
    SELECT 
        DATE_FORMAT(`aq`.`trx_date`, '%Y-%m-%d') AS `Fecha`,
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE))
            THEN
                (CASE
                    WHEN (`fi`.`tipo` = 33) THEN 1110401021
                    WHEN (`fi`.`tipo` = 110) THEN 1110401022
                    WHEN (`fi`.`tipo` = 39) THEN 1110401023
                    ELSE NULL
                END)
            ELSE 2120404002
        END) AS `cuenta`,
        CONCAT('Dunas Caja del ',
                DATE_FORMAT(`aq`.`trx_date`, '%Y-%m-%d')) AS `comentario`,
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE))
            THEN
                CONCAT('i   ',
                        (CASE
                            WHEN (`fi`.`rut` <> `fi`.`rut_defontana`) THEN 'Rut != '
                            ELSE ''
                        END),
                        `aq`.`confirmation_no`,
                        ' ',
                        `aq`.`pname`,
                        ' RM',
                        `aq`.`room`,
                        '.')
            ELSE CONCAT('i   ',
                    `aq`.`confirmation_no`,
                    ' ',
                    `aq`.`pname`,
                    ' RM',
                    `aq`.`room`)
        END) AS `glosa`,
        (CASE
            WHEN (`fi`.`total` < 0) THEN (`fi`.`total` * -(1))
            ELSE 0
        END) AS `debeMonedaPrincipal`,
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE))
            THEN
                (CASE
                    WHEN
                        (`fi`.`tipo` = 33)
                    THEN
                        (CASE
                            WHEN (`fi`.`total` > 0) THEN `fi`.`total`
                            ELSE 0
                        END)
                    WHEN
                        (`fi`.`tipo` = 110)
                    THEN
                        (CASE
                            WHEN (`fi`.`total` > 0) THEN `fi`.`total`
                            ELSE 0
                        END)
                    WHEN
                        (`fi`.`tipo` = 39)
                    THEN
                        (CASE
                            WHEN (`fi`.`total` > 0) THEN `fi`.`total`
                            ELSE 0
                        END)
                    ELSE NULL
                END)
            ELSE (CASE
                WHEN (`aq`.`amt` > 0) THEN `aq`.`amt`
                ELSE 0
            END)
        END) AS `haberMonedaPrincipal`,
        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`fi`.`rut_defontana`, '')
            ELSE ''
        END) AS `codigoDeFicha`,
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE))
            THEN
                (CASE
                    WHEN (`fi`.`tipo` = 39) THEN 'BEAV'
                    WHEN (`fi`.`tipo` = 33) THEN 'FEAV'
                    WHEN (`fi`.`tipo` = 61) THEN 'NCAV'
                    WHEN (`fi`.`tipo` = 110) THEN 'EEAV'
                    WHEN (`fi`.`tipo` = 112) THEN 'NCEV'
                    ELSE ''
                END)
            ELSE ''
        END) AS `tipoDeDocumento`,
        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`fi`.`folio`, 0)
            ELSE 0
        END) AS `numeroDeDocumento`,
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE))
            THEN
                COALESCE(DATE_FORMAT((`fi`.`fecha` + INTERVAL 30 DAY),
                                '%Y-%m-%d'),
                        '')
            ELSE ''
        END) AS `vencimientoDeDocto`,
        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`fi`.`rut_defontana`, '')
            ELSE ''
        END) AS `codigoLegal`,
        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) = CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`aq`.`pname`, '')
            ELSE ''
        END) AS `nombre`
    FROM
        (`dunasdb`.`arqueo` `aq`
        LEFT JOIN `dunasdb`.`fiscales` `fi` ON (((`aq`.`confirmation_no` = `fi`.`conf_no`)
            AND (`aq`.`fiscal_bill_no` = `fi`.`folio`))))
    WHERE
        ((1 = 1) AND (`aq`.`cashier_id` <> 9998)
            AND (`aq`.`trx_code` <> 9030)
            AND (`aq`.`trx_code` <> 9003)) 
    UNION ALL SELECT 
        DATE_FORMAT(`aq`.`trx_date`, '%Y-%m-%d') AS `Fecha`,
        (CASE
            WHEN (`aq`.`trx_code` = 9000) THEN 1110101001
            WHEN (`aq`.`trx_code` = 9004) THEN 1110402108
            WHEN (`aq`.`trx_code` = 9005) THEN 1110402102
            WHEN (`aq`.`trx_code` = 9006) THEN 1110402106
            WHEN (`aq`.`trx_code` = 9010) THEN 1110402101
            WHEN (`aq`.`trx_code` = 9014) THEN 1110402109
            WHEN (`aq`.`trx_code` = 9015) THEN 1110402103
            WHEN (`aq`.`trx_code` = 9016) THEN 1110402107
            ELSE 1110101001
        END) AS `cuenta`,
        CONCAT('Dunas Caja del ',
                DATE_FORMAT(`aq`.`trx_date`, '%Y-%m-%d')) AS `comentario`,
        CONCAT('ii  ',
                `aq`.`confirmation_no`,
                ' ',
                `aq`.`pname`,
                ' RM',
                `aq`.`room`,
                ' ',
                `aq`.`remark`,
                `aq`.`reference`) AS `glosa`,
        (CASE
            WHEN (`aq`.`amt` > 0) THEN `aq`.`amt`
            ELSE 0
        END) AS `debeMonedaPrincipal`,
        (CASE
            WHEN (`aq`.`amt` < 0) THEN (`aq`.`amt` * -(1))
            ELSE 0
        END) AS `haberMonedaPrincipal`,
        '' AS `codigoDeFicha`,
        '' AS `tipoDeDocumento`,
        0 AS `numeroDeDocumento`,
        '' AS `vencimientoDeDocto`,
        '' AS `codigoLegal`,
        '' AS `nombre`
    FROM
        (`dunasdb`.`arqueo` `aq`
        LEFT JOIN `dunasdb`.`fiscales` `fi` ON (((`aq`.`confirmation_no` = `fi`.`conf_no`)
            AND (`aq`.`fiscal_bill_no` = `fi`.`folio`))))
    WHERE
        ((1 = 1) AND (`aq`.`cashier_id` <> 9998)
            AND (`aq`.`trx_code` <> 9030)
            AND (`aq`.`trx_code` <> 9003)) 
    UNION ALL SELECT 
        DATE_FORMAT(`fi`.`fecha`, '%Y-%m-%d') AS `Fecha`,
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE))
            THEN
                (CASE
                    WHEN (`fi`.`tipo` = 33) THEN 1110401021
                    WHEN (`fi`.`tipo` = 110) THEN 1110401022
                    WHEN (`fi`.`tipo` = 39) THEN 1110401023
                    ELSE NULL
                END)
            ELSE 2120404002
        END) AS `cuenta`,
        CONCAT('Dunas Caja del ',
                DATE_FORMAT(`fi`.`fecha`, '%Y-%m-%d')) AS `comentario`,
        CONCAT('iii ',
                `aq`.`confirmation_no`,
                ' ',
                `aq`.`pname`,
                ' RM',
                `aq`.`room`,
                (CASE
                    WHEN (`fi`.`rut` <> `fi`.`rut_defontana`) THEN ' RUT != '
                    ELSE ''
                END)) AS `glosa`,
        (CASE
            WHEN (`fi`.`total` < 0) THEN (`fi`.`total` * -(1))
            ELSE 0
        END) AS `debeMonedaPrincipal`,
        (CASE
            WHEN (`fi`.`total` > 0) THEN `fi`.`total`
            ELSE 0
        END) AS `haberMonedaPrincipal`,
        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`fi`.`rut_defontana`, '')
            ELSE ''
        END) AS `codigoDeFicha`,
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE))
            THEN
                (CASE
                    WHEN (`fi`.`tipo` = 39) THEN 'BEAV'
                    WHEN (`fi`.`tipo` = 33) THEN 'FEAV'
                    WHEN (`fi`.`tipo` = 61) THEN 'NCAV'
                    WHEN (`fi`.`tipo` = 110) THEN 'EEAV'
                    WHEN (`fi`.`tipo` = 112) THEN 'NCEV'
                    ELSE ''
                END)
            ELSE ''
        END) AS `tipoDeDocumento`,
        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`fi`.`folio`, 0)
            ELSE ''
        END) AS `numeroDeDocumento`,
        (CASE
            WHEN
                (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE))
            THEN
                COALESCE(DATE_FORMAT((`fi`.`fecha` + INTERVAL 30 DAY),
                                '%Y-%m-%d'),
                        '')
            ELSE ''
        END) AS `vencimientoDeDocto`,
        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`fi`.`rut_defontana`, '')
            ELSE ''
        END) AS `codigoLegal`,
        (CASE
            WHEN (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE)) THEN COALESCE(`aq`.`pname`, '')
            ELSE ''
        END) AS `nombre`
    FROM
        (`dunasdb`.`fiscales` `fi`
        LEFT JOIN `dunasdb`.`arqueo` `aq` ON (((`aq`.`confirmation_no` = `fi`.`conf_no`)
            AND (`aq`.`fiscal_bill_no` = `fi`.`folio`)
            AND (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE))
            AND (`fi`.`total` = `aq`.`amt`))))
    WHERE
        ((1 = 1) AND (`aq`.`cashier_id` <> 9998)
            AND (`aq`.`trx_code` <> 9030)
            AND (`aq`.`trx_code` <> 9003)
            AND (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE))) 
    UNION ALL SELECT 
        DATE_FORMAT(`fi`.`fecha`, '%Y-%m-%d') AS `Fecha`,
        2120404002 AS `cuenta`,
        CONCAT('Dunas Caja del ',
                DATE_FORMAT(`fi`.`fecha`, '%Y-%m-%d')) AS `comentario`,
        CONCAT('iv  ',
                `aq`.`confirmation_no`,
                ' ',
                `aq`.`pname`,
                ' RM',
                `aq`.`room`,
                ' ',
                `aq`.`remark`,
                `aq`.`reference`) AS `glosa`,
        (CASE
            WHEN (`fi`.`total` > 0) THEN `aq`.`amt`
            ELSE 0
        END) AS `debeMonedaPrincipal`,
        (CASE
            WHEN (`fi`.`total` < 0) THEN (`aq`.`amt` * -(1))
            ELSE 0
        END) AS `haberMonedaPrincipal`,
        '' AS `codigoDeFicha`,
        '' AS `tipoDeDocumento`,
        '' AS `numeroDeDocumento`,
        '' AS `vencimientoDeDocto`,
        '' AS `codigoLegal`,
        '' AS `nombre`
    FROM
        (`dunasdb`.`fiscales` `fi`
        LEFT JOIN `dunasdb`.`arqueo` `aq` ON (((`aq`.`confirmation_no` = `fi`.`conf_no`)
            AND (`aq`.`fiscal_bill_no` = `fi`.`folio`)
            AND (`fi`.`total` = `aq`.`amt`))))
    WHERE
        ((1 = 1) AND (`aq`.`cashier_id` <> 9998)
            AND (`aq`.`trx_code` <> 9030)
            AND (`aq`.`trx_code` <> 9003)
            AND (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE))
            AND (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE))) 
    UNION ALL SELECT 
        DATE_FORMAT(`fi`.`fecha`, '%Y-%m-%d') AS `Fecha`,
        2120404002 AS `cuenta`,
        CONCAT('Dunas Caja del ',
                DATE_FORMAT(`fi`.`fecha`, '%Y-%m-%d')) AS `comentario`,
        CONCAT('v  ',
                `aq`.`confirmation_no`,
                ' ',
                `aq`.`pname`,
                ' RM',
                `aq`.`room`,
                ' ',
                `aq`.`remark`,
                `aq`.`reference`) AS `glosa`,
        (CASE
            WHEN (`fi`.`total` > 0) THEN `aq`.`amt`
            ELSE 0
        END) AS `debeMonedaPrincipal`,
        (CASE
            WHEN (`fi`.`total` < 0) THEN (`aq`.`amt` * -(1))
            ELSE 0
        END) AS `haberMonedaPrincipal`,
        '' AS `codigoDeFicha`,
        '' AS `tipoDeDocumento`,
        '' AS `numeroDeDocumento`,
        '' AS `vencimientoDeDocto`,
        '' AS `codigoLegal`,
        '' AS `nombre`
    FROM
        (`dunasdb`.`fiscales` `fi`
        LEFT JOIN `dunasdb`.`arqueo` `aq` ON (((`aq`.`confirmation_no` = `fi`.`conf_no`)
            AND (`aq`.`fiscal_bill_no` = `fi`.`folio`)
            AND (`fi`.`total` <> `aq`.`amt`))))
    WHERE
        ((1 = 1) AND (`aq`.`cashier_id` <> 9998)
            AND (`aq`.`trx_code` <> 9030)
            AND (`aq`.`trx_code` <> 9003)
            AND (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE))
            AND (CAST(`fi`.`fecha` AS DATE) > CAST(`aq`.`trx_date` AS DATE)))